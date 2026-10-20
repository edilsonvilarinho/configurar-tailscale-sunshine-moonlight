#!/usr/bin/env bash
# Restringe as portas do Sunshine a tailnet, tirando-as da rede local.
#
# Estrategia (ver guias/bazzite-host-tailscale-sunshine.html, etapa 8):
#   - tailscale0 fica na zona padrao permissiva  -> Sunshine acessivel pela tailnet
#   - a interface de LAN vai para uma zona nova  -> Sunshine inacessivel na rede de casa
# A interface tailscale0 nunca e tocada: trocar a zona dela derruba o link
# (tailscale/tailscale#15968).
#
# Uso:
#   bash scripts/bazzite-host-firewall-tailnet.sh            # dry-run (padrao)
#   bash scripts/bazzite-host-firewall-tailnet.sh --apply
#   bash scripts/bazzite-host-firewall-tailnet.sh --revert
#
# Variaveis opcionais:
#   ZONE=lan-restrito                          nome da zona criada
#   EXTRA_SERVICES="samba-client"              servicos extras liberados na LAN
#   EXTRA_PORTS="1714-1764/tcp 1714-1764/udp"  portas extras liberadas na LAN (ex.: KDE Connect)

set -euo pipefail

ZONE="${ZONE:-lan-restrito}"
MODE="dry-run"
case "${1:-}" in
  --apply)  MODE="apply" ;;
  --revert) MODE="revert" ;;
  ""|--dry-run) MODE="dry-run" ;;
  *) echo "Uso: $0 [--apply|--revert|--dry-run]" >&2; exit 2 ;;
esac

run() {
  if [[ "$MODE" == "dry-run" ]]; then
    printf '  [dry-run] %s\n' "$*"
  else
    printf '  + %s\n' "$*"
    "$@"
  fi
}

# Descobre as interfaces de LAN: tudo que nao e loopback, nem tailscale, nem virtual conhecida.
mapfile -t LAN_IFACES < <(
  ip -brief link show up \
    | awk '{print $1}' \
    | sed 's/@.*//' \
    | grep -vE '^(lo|tailscale[0-9]*|virbr[0-9]*|docker[0-9]*|podman[0-9]*|br-|veth|tun|wg)' \
    || true
)

if [[ ${#LAN_IFACES[@]} -eq 0 ]]; then
  echo "Nenhuma interface de LAN encontrada. Nada a fazer." >&2
  exit 1
fi

echo "Modo: $MODE"
echo "Zona: $ZONE"
echo "Interfaces de LAN detectadas: ${LAN_IFACES[*]}"

nm_connection_for() {
  nmcli -t -f DEVICE,NAME connection show --active 2>/dev/null \
    | awk -F: -v dev="$1" '$1==dev {print $2; exit}'
}

if [[ "$MODE" == "revert" ]]; then
  echo
  echo "Devolvendo as interfaces de LAN a zona padrao:"
  for iface in "${LAN_IFACES[@]}"; do
    conn="$(nm_connection_for "$iface")"
    if [[ -n "$conn" ]]; then
      run sudo nmcli connection modify "$conn" connection.zone ""
      run sudo nmcli connection up "$conn"
    else
      run sudo firewall-cmd --zone="$ZONE" --remove-interface="$iface"
    fi
  done
  echo
  echo "A zona '$ZONE' continua existindo (vazia). Para apaga-la:"
  echo "  sudo firewall-cmd --permanent --delete-zone=$ZONE && sudo firewall-cmd --reload"
  exit 0
fi

# --- criacao da zona restrita ---
echo
echo "1) Zona restrita"
if firewall-cmd --get-zones 2>/dev/null | tr ' ' '\n' | grep -qx "$ZONE"; then
  echo "  (a zona '$ZONE' ja existe)"
else
  run sudo firewall-cmd --permanent --new-zone="$ZONE"
fi

# Servicos minimos para a rede local continuar utilizavel.
SERVICES=(dhcpv6-client mdns)
# Se o SSH esta ligado, mante-lo acessivel pela LAN evita perder acesso remoto.
if systemctl is-enabled --quiet sshd 2>/dev/null; then
  SERVICES+=(ssh)
  echo "  (sshd habilitado: o servico ssh sera mantido liberado na LAN)"
fi
# shellcheck disable=SC2206
SERVICES+=(${EXTRA_SERVICES:-})

for svc in "${SERVICES[@]}"; do
  [[ -n "$svc" ]] && run sudo firewall-cmd --permanent --zone="$ZONE" --add-service="$svc"
done

# shellcheck disable=SC2206
PORTS=(${EXTRA_PORTS:-})
for port in "${PORTS[@]}"; do
  [[ -n "$port" ]] && run sudo firewall-cmd --permanent --zone="$ZONE" --add-port="$port"
done

run sudo firewall-cmd --reload

# --- prende a zona na conexao do NetworkManager ---
echo
echo "2) Interfaces de LAN -> $ZONE"
for iface in "${LAN_IFACES[@]}"; do
  conn="$(nm_connection_for "$iface")"
  if [[ -n "$conn" ]]; then
    echo "  $iface (conexao NetworkManager: $conn)"
    run sudo nmcli connection modify "$conn" connection.zone "$ZONE"
    run sudo nmcli connection up "$conn"
  else
    echo "  $iface (sem conexao NetworkManager ativa; aplicando direto no firewalld)"
    run sudo firewall-cmd --permanent --zone="$ZONE" --add-interface="$iface"
    run sudo firewall-cmd --reload
  fi
done

echo
echo "3) Estado resultante"
if [[ "$MODE" == "apply" ]]; then
  firewall-cmd --get-active-zones
  echo
  firewall-cmd --list-all --zone="$ZONE"
  echo
  echo "Verifique agora, de fora:"
  echo "  na LAN     -> nc -vz <ip-lan>  47990   (deve FALHAR)"
  echo "  na tailnet -> nc -vz <ip-100.x> 47990  (deve CONECTAR)"
else
  echo "  (dry-run: nada foi alterado; rode com --apply para valer)"
fi
