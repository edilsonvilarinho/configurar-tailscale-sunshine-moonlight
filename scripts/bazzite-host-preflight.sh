#!/usr/bin/env bash
# Pre-validacao do host Bazzite para Tailscale + Sunshine.
# Somente leitura: nao instala, nao altera configuracao, nao pede sudo.
# Uso: bash scripts/bazzite-host-preflight.sh

set -uo pipefail

section() { printf '\n\033[1m=== %s ===\033[0m\n' "$1"; }
value()   { printf '  %-28s %s\n' "$1" "$2"; }
missing() { printf '  %-28s \033[33m%s\033[0m\n' "$1" "$2"; }

unit_state() { systemctl "$@" 2>/dev/null || true; }

section "Sistema"
value "Host" "$(hostname)"
value "Imagem" "$(grep -E '^PRETTY_NAME=' /etc/os-release | cut -d= -f2- | tr -d '\"')"
value "Variante" "$(grep -E '^VARIANT_ID=' /etc/os-release | cut -d= -f2- | tr -d '\"')"
value "Kernel" "$(uname -r)"
if command -v rpm-ostree >/dev/null; then
  value "Deployment" "$(rpm-ostree status --booted 2>/dev/null | grep -E 'Version:' | head -1 | xargs)"
fi

section "Sessao grafica"
value "XDG_SESSION_TYPE" "${XDG_SESSION_TYPE:-<vazio>}"
value "XDG_CURRENT_DESKTOP" "${XDG_CURRENT_DESKTOP:-<vazio>}"
if [[ "${XDG_SESSION_TYPE:-}" != "wayland" ]]; then
  missing "Atencao" "a captura via KWin Screencast espera uma sessao Wayland"
fi
value "Autologin SDDM" "$(ls /etc/sddm.conf.d/ 2>/dev/null | tr '\n' ' ' || echo '<nao configurado>')"
value "Linger do usuario" "$(loginctl show-user "$USER" -p Linger --value 2>/dev/null || echo '?')"

section "GPU"
lspci 2>/dev/null | grep -iE 'vga|3d' | sed 's/^/  /'
if command -v nvidia-smi >/dev/null; then
  value "Driver NVIDIA" "$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -1)"
fi

section "Monitores"
if command -v kscreen-doctor >/dev/null; then
  kscreen-doctor -o 2>/dev/null \
    | sed 's/\x1b\[[0-9;]*m//g' \
    | awk '
        /^Output:/ { name = $3 }
        /Modes:/   { for (i = 1; i <= NF; i++) if ($i ~ /\*$/) { split($i, m, ":"); print "  " name "  " m[2] } }
      '
else
  missing "kscreen-doctor" "nao encontrado"
fi

section "Tailscale"
if command -v tailscale >/dev/null; then
  value "Versao" "$(tailscale version | head -1)"
  value "Servico tailscaled" "$(unit_state is-enabled tailscaled)/$(unit_state is-active tailscaled)"
  if systemctl is-active --quiet tailscaled; then
    value "IPv4 da tailnet" "$(tailscale ip -4 2>/dev/null | head -1 || echo '<sem login>')"
    tailscale status 2>/dev/null | sed 's/^/  /' | head -15
  else
    missing "Estado" "tailscaled parado — rode: ujust tailscale enable"
  fi
else
  missing "tailscale" "nao encontrado na imagem"
fi

section "Sunshine"
if flatpak info dev.lizardbyte.app.Sunshine >/dev/null 2>&1; then
  value "Flatpak" "$(flatpak info dev.lizardbyte.app.Sunshine 2>/dev/null | grep -i '^ *Version:' | xargs)"
  value "Servico de usuario" "$(unit_state --user is-enabled app-dev.lizardbyte.app.Sunshine)/$(unit_state --user is-active app-dev.lizardbyte.app.Sunshine)"
  CONF="$HOME/.var/app/dev.lizardbyte.app.Sunshine/config/sunshine/sunshine.conf"
  if [[ -f "$CONF" ]]; then
    value "sunshine.conf" "$CONF"
    grep -E '^(origin_web_ui_allowed|csrf_allowed_origins|upnp|capture|output_name|encoder)' "$CONF" 2>/dev/null | sed 's/^/    /'
  else
    missing "sunshine.conf" "ainda nao existe (so nasce no primeiro arranque)"
  fi
else
  missing "Sunshine" "nao instalado — rode: ujust setup-sunshine (Enable (Flatpak))"
fi

section "Portas em escuta"
for p in 47984 47989 47990 48010; do
  if ss -ltn 2>/dev/null | grep -q ":$p "; then value "TCP $p" "escutando"; else missing "TCP $p" "fechada"; fi
done
for p in 47998 47999 48000; do
  if ss -lun 2>/dev/null | grep -q ":$p "; then value "UDP $p" "escutando"; else missing "UDP $p" "fechada"; fi
done

section "Firewall"
value "firewalld" "$(systemctl is-active firewalld 2>/dev/null || echo '?')"
value "Zona padrao" "$(firewall-cmd --get-default-zone 2>/dev/null || echo '<sem permissao>')"
firewall-cmd --get-active-zones 2>/dev/null | sed 's/^/  /'
if firewall-cmd --get-default-zone 2>/dev/null | grep -q FedoraWorkstation; then
  missing "Observacao" "FedoraWorkstation libera TCP/UDP 1025-65535 em todas as interfaces"
fi

section "Interfaces"
ip -brief addr show 2>/dev/null | sed 's/^/  /'

printf '\nPre-validacao concluida. Nada foi alterado.\n'
