# Plano de configuração remota: Tailscale + Sunshine + Moonlight

## Resumo

O guia está correto na arquitetura geral, mas precisa de ajustes antes da execução:

- `tailscale ip -4` e o pareamento via PIN estão corretos.
- O caminho fixo `C:\\Program Files\\Sunshine` não deve ser presumido.
- `Get-Process sunshine` não é suficiente; a instalação atual usa serviço do Windows.
- A lista de portas está incompleta; falta principalmente a TCP `48010`.
- `senha_temporaria123` é fraca e não será usada.
- O aviso de certificado do Sunshine é esperado porque o certificado é autoassinado.
- Os colchetes na URL são apenas notação: para IPv4 será `https://100.x.x.x:47990`.

## Etapas planejadas

### 1. Pré-validação no host

Executar PowerShell como Administrador e registrar versão do Windows, arquitetura, WinGet, Tailscale, Sunshine, serviço existente, regras de firewall, driver NVIDIA e display ativo.

O host precisará permanecer ligado e não suspender durante o uso remoto. Se o Sunshine não encontrar display ou encoder, o log será analisado antes de qualquer alteração adicional.

### 2. Instalar e autenticar o Tailscale

Usar o identificador exato:

```powershell
winget install --id Tailscale.Tailscale --exact --source winget `
  --accept-package-agreements --accept-source-agreements `
  --silent --disable-interactivity
```

Localizar dinamicamente `tailscale.exe`, executar `tailscale up`, capturar o link de autenticação quando exibido e aguardar a aprovação do dispositivo pelo usuário.

Validar:

```powershell
& $tailscale status
& $tailscale ip -4
& $tailscale netcheck
```

Salvar o IP Tailscale no relatório final. Se necessário, usar o login pela bandeja do Windows ou `tailscale login`.

### 3. Instalar o Sunshine

Se não houver instalação existente:

```powershell
winget install --id LizardByte.Sunshine --exact --source winget `
  --accept-package-agreements --accept-source-agreements `
  --silent --disable-interactivity
```

Descobrir o executável e o diretório de configuração pelo registro, serviço e caminho real. Não assumir `C:\\Program Files\\Sunshine`.

Usar o serviço instalado pelo pacote. Não executar `Start-Process sunshine.exe` se o serviço já estiver ativo, evitando uma segunda instância.

Validar portas em escuta:

- TCP `47984`, `47989`, `47990`, `48010`;
- UDP `47998`, `47999`, `48000`.

### 4. Criar credenciais seguras

Parar temporariamente o serviço, manter o usuário `admin`, gerar uma senha aleatória forte com pelo menos 24 caracteres e executar `sunshine.exe --creds admin <senha>`.

Iniciar novamente o serviço e validar o login. A senha não será registrada em logs. Depois do primeiro acesso, o usuário deverá alterá-la na Web UI. A senha fixa `senha_temporaria123` não será utilizada.

### 5. Configurar o firewall somente para Tailscale

Descobrir o alias real da interface Tailscale e auditar regras existentes do Sunshine.

Criar ou ajustar regras idempotentes vinculadas ao executável do Sunshine e à interface Tailscale:

- Web UI: TCP `47990`;
- Sunshine/Moonlight: TCP `47984`, `47989`, `48010`;
- vídeo, controle e áudio: UDP `47998`, `47999`, `48000`;
- microfone: UDP `48002` somente se necessário.

Não abrir UDP `5353` inicialmente, pois o cliente será adicionado manualmente pelo IP Tailscale. Regras genéricas antigas que permitam essas portas em qualquer interface serão restringidas ou desabilitadas seletivamente.

### 6. Liberar a Web UI remotamente

Testar primeiro com `origin_web_ui_allowed = lan`. Se o IP Tailscale for recusado, fazer backup de `sunshine.conf`, confirmar UPnP desabilitado, ajustar `origin_web_ui_allowed = wan` e manter o firewall exclusivamente na interface Tailscale.

Se a Web UI abrir mas não aceitar alterações, adicionar `https://<ip-tailscale>:47990` em `csrf_allowed_origins` e reiniciar o serviço.

### 7. Configurar o cliente Windows

```powershell
winget install --id Tailscale.Tailscale --exact --source winget `
  --accept-package-agreements --accept-source-agreements `
  --silent --disable-interactivity

winget install --id MoonlightGameStreamingProject.Moonlight --exact `
  --source winget --accept-package-agreements `
  --accept-source-agreements --silent --disable-interactivity
```

Entrar no Tailscale com a mesma conta, confirmar o host online, abrir `https://100.x.x.x:47990`, aceitar o certificado autoassinado, alterar a senha e adicionar o host no Moonlight pelo IP Tailscale.

No pareamento, copiar o PIN do Moonlight, abrir a aba `PIN` do Sunshine, inserir o PIN e nomear o dispositivo.

### 8. Teste funcional final

Confirmar conectividade Tailscale, Web UI, serviço Sunshine, portas, pareamento, lista de aplicações, vídeo, áudio, teclado, mouse, controle, reconexão e estabilidade da sessão.

O relatório final deverá conter IP Tailscale, nome do dispositivo, versões, serviço, portas, URL, resultado do pareamento, teste de streaming e alterações realizadas.

Antes de alterar configuração ou firewall, salvar backup de `sunshine.conf` e registrar regras existentes. Em caso de falha, restaurar a configuração e remover somente as regras criadas pelo procedimento.

## Registro da execução — 23/09/2026

### Topologia confirmada

- Host Sunshine: `sammysan` / Windows 11 25H2.
- IP Tailscale do host: `100.78.107.32`.
- Cliente Windows: `NOTE-LAT-012`.
- IP Tailscale do cliente: `100.114.232.6`.
- GPU do host: NVIDIA GeForce RTX 4070 SUPER.
- Sunshine instalado: `2026.914.233613`.
- Conta Tailscale: mesma tailnet nos dois computadores.

Não registrar neste arquivo senhas, tokens ou PINs. A senha do Sunshine foi criada durante a configuração, mas o segredo foi omitido deliberadamente.

### O que foi validado no host

1. Tailscale instalado e autenticado; o host recebeu `100.78.107.32`.
2. Sunshine instalado como serviço `SunshineService`, com inicialização automática.
3. Sunshine escutando nos seguintes endereços/portas:

   - TCP `47984`, `47989`, `47990`, `48010`;
   - UDP `47998`, `47999`, `48000`.

4. A Web UI respondeu localmente com HTTP `401`, comportamento esperado antes da autenticação:

   ```powershell
   Test-NetConnection 127.0.0.1 -Port 47990
   Test-NetConnection 100.78.107.32 -Port 47990
   ```

5. `origin_web_ui_allowed = wan` foi mantido para permitir o acesso pela origem Tailscale. O UPnP ficou desativado:

   ```text
   origin_web_ui_allowed = wan
   upnp = disabled
   ```

   Isso não substitui o firewall; as regras de entrada continuam limitadas à interface Tailscale e ao cliente conhecido.

### Diagnóstico reproduzido da falha de rede

O primeiro teste no cliente falhou:

```powershell
Test-NetConnection 100.78.107.32 -Port 47990 -InformationLevel Quiet
# False
```

Foi incorreto testar `127.0.0.1` no cliente para validar o Sunshine: esse endereço sempre representa a própria máquina onde o comando é executado. No cliente, o destino correto é `100.78.107.32`.

Foi feita captura PktMon no host durante uma nova tentativa. A captura comprovou:

- os SYNs de `100.114.232.6` chegaram pela interface `Tailscale`;
- o descarte ocorreu no host, no componente `107`, identificado como `tcpip.sys`, endereço local `100.78.107.32`;
- o motivo registrado foi `INET: accept inspection`;
- não era falha de autenticação Tailscale nem ausência do listener Sunshine.

Também foi confirmado que, ao desativar o firewall do host, o teste do cliente passou. Isso isolou o problema no Firewall do Windows do `sammysan`. O firewall não deve permanecer desativado.

### Causa encontrada no firewall

O perfil `Private`, usado pela interface Tailscale, estava com:

```text
Enabled = True
DefaultInboundAction = Block
AllowInboundRules = False
AllowLocalFirewallRules = True
```

Assim, as regras locais Allow do Sunshine eram ignoradas. A correção aplicada foi:

1. manter o Firewall do Windows ativado;
2. manter `DefaultInboundAction = Block`;
3. definir `AllowInboundRules = True` somente no perfil `Private`;
4. desativar as regras genéricas que permitiam Sunshine para qualquer origem Tailscale;
5. manter regras específicas para:
   - interface `Tailscale`;
   - destino local `100.78.107.32`;
   - origem remota `100.114.232.6`;
   - TCP `47984,47989,47990,48010`;
   - UDP `47998,47999,48000`.

Regras finais criadas/ajustadas:

```text
Sunshine via Tailscale NOTE-LAT-012 TCP
Sunshine via Tailscale NOTE-LAT-012 UDP
```

As regras genéricas `Sunshine via Tailscale TCP` e `Sunshine via Tailscale UDP` foram desativadas para preservar o escopo mínimo.

### Diagnóstico e correção do erro CSRF

Depois que a rede funcionou, o Moonlight encontrou o host e gerou um PIN, mas o envio pela Web UI exibiu:

```text
CSRF Protection Error
To allow this origin, add it to the 'csrf_allowed_origins' option
```

Esse erro ocorreu porque a Web UI estava sendo acessada por `https://100.78.107.32:47990`, uma origem adicional não incluída nos padrões locais do Sunshine. A correção aplicada no host foi:

```text
csrf_allowed_origins = https://100.78.107.32:47990
```

O serviço `SunshineService` foi reiniciado. Após a reinicialização, a porta `47990` voltou a escutar e o PIN foi aceito.

Foi criado backup antes da alteração:

```text
C:\Program Files\Sunshine\config\sunshine.conf.backup-20260923-150033
```

### Resultado final confirmado

- Cliente acessou a Web UI do Sunshine pelo IP Tailscale.
- Moonlight encontrou o host `sammysan`.
- Pareamento PIN concluído com sucesso.
- Moonlight exibiu as aplicações `Desktop` e `Steam`.
- Firewall do host permaneceu ativado.
- Nenhuma porta pública ou port forwarding foi configurado.

### Sequência correta para repetir a configuração

1. No host, instalar/autenticar Tailscale e anotar o IP `100.x.x.x`.
2. Instalar Sunshine e confirmar o serviço e os listeners.
3. Criar credencial forte; nunca usar a senha fixa do guia original.
4. Confirmar a interface Tailscale e o perfil de rede.
5. Antes de testar o cliente, garantir no perfil privado do host:

   ```powershell
   Get-NetFirewallProfile -PolicyStore ActiveStore -Name Private |
       Select-Object Name,Enabled,DefaultInboundAction,AllowInboundRules,AllowLocalFirewallRules
   ```

   O esperado é `Enabled=True`, `DefaultInboundAction=Block`, `AllowInboundRules=True` e `AllowLocalFirewallRules=True`.

6. Criar regras de entrada restritas ao IP Tailscale do cliente e às portas Sunshine. Não confiar apenas em regras com o nome `Sunshine`; conferir filtros de endereço, interface e portas.
7. Configurar `csrf_allowed_origins` com a origem exata usada no navegador e reiniciar o Sunshine antes do pareamento.
8. No cliente, instalar Tailscale e Moonlight, entrar na mesma tailnet e testar:

   ```powershell
   tailscale ping 100.78.107.32
   Test-NetConnection 100.78.107.32 -Port 47990 -InformationLevel Detailed
   ```

9. Abrir `https://100.78.107.32:47990`, atualizar a página após qualquer mudança de configuração, inserir o PIN na aba `PIN` e validar `Desktop`/`Steam`.
10. Só considerar concluído depois de validar imagem, áudio, mouse/teclado e, se necessário, controle.

### Próxima expansão: tablet

O tablet pode usar Tailscale + Moonlight, sem Sunshine. Porém, o firewall atual permite especificamente apenas `100.114.232.6`. Ao adicionar um tablet:

1. instalar Tailscale no tablet e entrar na mesma tailnet;
2. obter o novo IP `100.x.x.x` do tablet;
3. criar no host regras TCP/UDP equivalentes, restritas a esse novo IP;
4. adicionar `100.78.107.32` no Moonlight do tablet e parear.

Não ampliar automaticamente para toda a faixa `100.64.0.0/10` sem avaliar o risco: isso permitiria que qualquer dispositivo autorizado na tailnet alcançasse o Sunshine.

### Arquivos de execução e evidências

Os scripts administrativos usados na execução ficaram em `planos/` e fazem validações de hostname antes de alterar o host:

- `bootstrap-elevated.ps1`;
- `configure-sunshine-elevated.ps1`;
- `restrict-sunshine-host-firewall-elevated.ps1`;
- `allow-sunshine-tailscale-origin-elevated.ps1`;
- `guia-maquina-cliente-tailscale-moonlight.md`.

As capturas PktMon e os logs permanecem na pasta para auditoria. Não reutilizar logs que possam conter credenciais; senhas e PINs não fazem parte do plano.

### Referências oficiais consultadas

- Sunshine — configuração e `csrf_allowed_origins`: <https://github.com/LizardByte/Sunshine/blob/master/docs/configuration.md>
- Sunshine — API e proteção CSRF: <https://github.com/LizardByte/Sunshine/blob/master/docs/api.md>
- Tailscale — instalação: <https://tailscale.com/docs/install>
- Moonlight — guia de configuração: <https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide>
