# Tailscale + Sunshine + Moonlight

Procedimentos para jogar remotamente com Sunshine no host e Moonlight no cliente, com os dois lados
se enxergando apenas pela tailnet — sem port forwarding e sem porta pública.

## Host Bazzite (Linux)

- [Guia de instalação passo a passo (HTML)](guias/bazzite-host-tailscale-sunshine.html)
- [Plano, decisões e pontos de situação](planos/configurar-bazzite-sunshine-tailscale-moonlight.md)
- Scripts de apoio:
  - `scripts/bazzite-host-preflight.sh` — pré-validação somente leitura do host
  - `scripts/bazzite-host-firewall-tailnet.sh` — restringe as portas do Sunshine à tailnet (`--apply` / `--revert`)

## Host Windows

- [Plano e registro da execução](planos/configurar-tailscale-sunshine-moonlight.md)
- Scripts PowerShell em `planos/*.ps1`

## Cliente

- [Guia da máquina cliente (Tailscale + Moonlight)](planos/guia-maquina-cliente-tailscale-moonlight.md)

## Regra válida para todos os documentos

Senha, token e PIN não entram neste repositório.
