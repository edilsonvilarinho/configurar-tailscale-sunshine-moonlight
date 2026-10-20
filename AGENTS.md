# Instruções para agentes de IA

Este arquivo é lido automaticamente por Claude Code, Codex, Cursor e outros agentes. Ele descreve
como **executar** a configuração descrita neste repositório, não apenas como explicá-la.

Humano lendo isto: você não precisa deste arquivo. Siga o [`README.md`](README.md).

---

## Objetivo

Transformar o host Linux em servidor de streaming de jogos (Sunshine), alcançável **somente**
pela rede privada Tailscale, e parear ao menos um cliente Moonlight.

## Regras inegociáveis

1. **Nunca** abra porta no roteador, não habilite UPnP e não desative o firewall "para testar".
2. **Nunca** escreva senha, token ou PIN em arquivo do repositório, em log, em commit ou na sua
   resposta. Se o usuário informar uma senha no chat, avise que ela ficou exposta ali e recomende
   trocá-la ao final.
3. **Não** troque a zona de firewall da interface `tailscale0`: derruba o link
   ([tailscale#15968](https://github.com/tailscale/tailscale/issues/15968)).
4. **Peça confirmação explícita** antes de: ligar login automático, mascarar a suspensão, e
   aplicar a restrição de firewall na placa de rede local.
5. Faça **cópia de segurança** de `sunshine.conf` antes de qualquer edição.
6. Verifique cada passo antes de seguir para o próximo. Não presuma sucesso a partir do código de
   saída de um comando que não mede o que importa.
7. Se um passo falhar, **pare e relate**. Não contorne com solução mais permissiva.

## Pré-condições que você deve checar antes de começar

```bash
grep -E '^(PRETTY_NAME|VARIANT_ID)=' /etc/os-release   # espera-se Bazzite
echo $XDG_SESSION_TYPE $XDG_CURRENT_DESKTOP            # espera-se: wayland KDE
```

Se não for Bazzite, avise: os comandos `ujust` não existirão e os caminhos podem mudar. Se a
sessão não for Wayland+KDE, a captura e o monitor virtual mudam de comportamento — relate antes
de prosseguir.

## Como obter privilégio (importante)

`sudo` vai pedir senha e **você não consegue digitá-la**. Duas saídas, nesta ordem de preferência:

1. **Peça ao usuário** que rode o comando, indicando exatamente qual é.
2. **Abra um terminal na sessão gráfica dele** e deixe o `sudo` pedir a senha lá:
   ```bash
   setsid konsole -e bash /caminho/para/script.sh      # KDE
   setsid gnome-terminal -- bash /caminho/para/script.sh
   ```

**Não use `pkexec`.** A partir de um shell automatizado o polkit responde `Not authorized` sem
abrir diálogo, porque não há agente de autenticação atrelado ao seu processo. Isso já foi testado
aqui e não funciona.

---

## Procedimento

Cada passo traz o comando e **como verificar**. O guia completo, com o porquê de cada decisão,
está em [`guias/bazzite-host-tailscale-sunshine.html`](guias/bazzite-host-tailscale-sunshine.html).

### 1. Inventário (não altera nada)

```bash
bash scripts/bazzite-host-preflight.sh
```
Relate ao usuário o estado encontrado antes de modificar qualquer coisa.

### 2. Tailscale

```bash
ujust tailscale enable                 # precisa de sudo
sudo tailscale up --operator=$USER     # imprime link de login
```
O link `https://login.tailscale.com/a/…` precisa ser aberto **pelo usuário**, no navegador.
Entregue o link e aguarde.

**Verificação:** `tailscale ip -4` devolve um endereço `100.x.y.z`. Guarde-o; os passos seguintes
usam esse valor.

### 3. Sunshine

```bash
ujust setup-sunshine        # opção: Enable (Flatpak)
```
Equivale a `flatpak install --system`, depois `additional-install.sh` (permissões de `uinput`) e
`systemctl --user enable --now app-dev.lizardbyte.app.Sunshine`.

**Verificação:** `ss -ltn | grep -E ':(47984|47989|47990|48010) '` lista as quatro portas.

### 4. Interface web pela tailnet

```bash
CONF=~/.var/app/dev.lizardbyte.app.Sunshine/config/sunshine/sunshine.conf
cp -a "$CONF" "$CONF.backup-$(date +%Y%m%d-%H%M%S)"
printf 'origin_web_ui_allowed = wan\nupnp = disabled\n' >> "$CONF"
printf 'csrf_allowed_origins = https://%s:47990\n' "$(tailscale ip -4)" >> "$CONF"
systemctl --user restart app-dev.lizardbyte.app.Sunshine
```
Se a chave já existir no arquivo, **edite a linha** em vez de acrescentar outra.

**Verificação:** `curl -sk -o /dev/null -w '%{http_code}\n' https://$(tailscale ip -4):47990/`
deve responder `401` (exige login) — e não falha de conexão.

### 5. Credenciais

A senha é do usuário. **Não a invente nem a peça no chat.** Abra a interface e deixe que ele a
crie:

```bash
xdg-open https://localhost:47990
```
Oriente: senha forte, diferente da senha do sistema. O aviso de certificado autoassinado é normal.

**Verificação:** `grep -o '"username"[^,]*' ~/.var/app/dev.lizardbyte.app.Sunshine/config/sunshine/sunshine_state.json`

### 6. Firewall (confirme antes)

No Bazzite a zona padrão já libera TCP/UDP 1025-65535 em todas as interfaces. O trabalho é
**fechar** para a rede local, mantendo a tailnet.

```bash
bash scripts/bazzite-host-firewall-tailnet.sh            # simulação, mostre a saída ao usuário
bash scripts/bazzite-host-firewall-tailnet.sh --apply    # só após confirmação
```
Avise que isso bloqueia entrada da LAN em portas altas (KDE Connect, Steam Remote Play local).
Para desfazer: `--revert`.

**Verificação:** `firewall-cmd --get-zone-of-interface=tailscale0` deve dizer `no zone`, e
`tailscale ip -4` deve continuar respondendo.

### 7. Monitor capturado

Com mais de um monitor, o erro é silencioso: sem `output_name`, o Sunshine captura o primeiro
fluxo, que pode ser a tela errada.

```bash
grep '\[wayland\] Name' ~/.var/app/dev.lizardbyte.app.Sunshine/config/sunshine/sunshine.log | tail -4
echo 'output_name = DP-1' >> "$CONF"      # use o nome correto
systemctl --user restart app-dev.lizardbyte.app.Sunshine
```
Pergunte ao usuário **qual** monitor ele quer transmitir antes de escolher.

**Verificação:** a linha `Streaming display '<nome>'` no log, após o reinício.

### 8. Host sempre pronto (confirme cada item)

O Sunshine é serviço de usuário: sem sessão gráfica aberta, não há captura.

```bash
sudo tee /etc/sddm.conf.d/10-autologin.conf    # login automático — RISCO: acesso físico sem senha
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
loginctl enable-linger $USER
```
Explique o custo do login automático e **só aplique se o usuário aceitar**.

### 9. Pareamento

O usuário instala Tailscale + Moonlight no aparelho, adiciona o host pelo endereço `100.x.y.z` e
obtém um PIN de 4 dígitos. Você pode enviá-lo pela API, o que evita o erro de CSRF do navegador:

```bash
curl -sk -u admin:'<senha>' -X POST https://localhost:47990/api/pin \
  -d '{"pin":"1234","name":"<apelido>"}'
```
Peça a senha ao usuário **no momento do uso** e não a repita na sua resposta.

**Verificação:** `curl -sk -u admin:'<senha>' https://localhost:47990/api/clients/list`

---

## Erros conhecidos, e o que eles significam

| Mensagem | Significado | Ação |
|---|---|---|
| `Failed to gain CAP_SYS_ADMIN` | **ruído**: sonda de captura KMS no Flatpak | ignore; o próprio log diz isso |
| `setpriority failed for nice -15` | prioridade de thread negada | não impede streaming |
| Erro 503 / `Failed to find display` | KWin recusou a captura | `KWIN_WAYLAND_NO_PERMISSION_CHECKS=1` + relogin |
| `CSRF Protection Error` | origem não autorizada | `csrf_allowed_origins` com o endereço exato |
| `Not authorized` do pkexec | sem agente polkit para o seu processo | use terminal na sessão do usuário |

## Ao final, relate

- endereço `100.x.y.z` do host e nome na tailnet;
- estado dos serviços `tailscaled` e `app-dev.lizardbyte.app.Sunshine`;
- zonas de firewall de cada interface;
- quais clientes estão pareados;
- o que **não** foi aplicado e por quê;
- lembrete de trocar qualquer senha que tenha passado pelo chat.

## Se for registrar o trabalho em commit

Conventional Commits em inglês. Comentário em português. Nunca inclua segredo na mensagem.
