# CLAUDE.md

As instruções deste repositório para agentes estão em [`AGENTS.md`](AGENTS.md). Leia aquele
arquivo antes de executar qualquer configuração.

Resumo do que não pode ser esquecido:

- Nunca abrir porta no roteador, nunca desativar o firewall, nunca habilitar UPnP.
- Nunca gravar senha, token ou PIN em arquivo, log, commit ou resposta.
- Não trocar a zona de firewall da interface `tailscale0` (derruba o link).
- `pkexec` não funciona a partir de shell automatizado: peça ao usuário, ou abra um terminal na
  sessão gráfica dele.
- Confirmar com o usuário antes de login automático, de mascarar suspensão e de restringir a LAN.
