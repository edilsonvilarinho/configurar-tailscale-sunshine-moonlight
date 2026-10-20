# CLAUDE.md

As instruções deste repositório para agentes estão em [`AGENTS.md`](AGENTS.md). Leia aquele
arquivo antes de executar qualquer configuração. Ele cobre **as duas plataformas**:

- **Parte A** — host Bazzite (Linux)
- **Parte B** — host Windows
- **Parte C** — cliente Moonlight, em qualquer sistema

Resumo do que não pode ser esquecido:

- Nunca abrir porta no roteador, nunca desativar o firewall, nunca habilitar UPnP.
- Nunca gravar senha, token ou PIN em arquivo, log, commit ou resposta.
- Linux: não trocar a zona de firewall da interface `tailscale0` (derruba o link); `pkexec` não
  funciona a partir de shell automatizado — peça ao usuário ou abra um terminal na sessão dele.
- Windows: o perfil `Private` com `AllowInboundRules=False` faz o sistema ignorar as regras de
  Allow em silêncio; e os `planos/*.ps1` só rodam na máquina original (validam o hostname).
- Confirmar com o usuário antes de login automático, de impedir a suspensão e de restringir a LAN.
