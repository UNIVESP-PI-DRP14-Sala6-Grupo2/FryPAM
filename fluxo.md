Fluxo de Retirada de Senha (Passo a Passo)

1. Funcionário Solicita Acesso
 - Ação:
   * O funcionário faz login no sistema PAM.
   * Seleciona a conta AWS que precisa acessar.
   * Especifica uma janela de tempo (1–4 horas) durante a qual retirará a senha.
 - Resposta do Sistema:
   * Cria uma solicitação pendente e notifica o validador designado por e-mail.

2. Validador Aprova/Nega
 - Ação do Validador:
   * Faz login no sistema PAM para revisar a solicitação.
   * Verifica a justificativa e a janela de tempo.
   * Aprova ou nega a solicitação.
 - Resposta do Sistema (se aprovado):
   * Ativa a janela de retirada (inicia o cronômetro).
   * Agenda uma rotação automática de senha no final da janela.
   * Notifica o funcionário de que o acesso foi concedido.

3. Funcionário Retira a Senha (Uma Vez)
 - Ação do Funcionário:
   * Faz login no sistema PAM dentro da janela aprovada.
   * Navega até sua solicitação aprovada e clica em "Retirar Senha".
 - Resposta do Sistema:
   * Gera uma nova senha usando o AWS SDK.
   * Rotaciona a senha da conta AWS imediatamente (credenciais antigas são invalidadas).
   * Exibe a nova senha uma única vez na tela (não armazenada no sistema).
   * Marca a solicitação como usada.

4. Expiração da Senha e Rotação Automática
 - Se o funcionário retirar a senha:
   * A senha se torna inválida após um uso (mesmo que a janela ainda esteja aberta).
 -  Se a janela expirar sem uso:
   * O sistema gera automaticamente uma nova senha via AWS SDK (não mostrada a ninguém).
   * Marca a solicitação como expirada.

____

Regras Chave
 * Acesso Único: As senhas são exibidas uma vez e rotacionadas imediatamente.
 * Tempo Limite: A retirada é permitida somente durante a janela aprovada.
 * Sem Armazenamento: As senhas existem temporariamente na memória e nunca são salvas.
 * Trilha de Auditoria: Todas as ações (solicitações, aprovações, retiradas) são registradas para conformidade.
Fluxo Visual
Funcionário → Solicitação → Validador → Aprovar → (Janela Abre) → Retirar → Senha Exibida → Rotação Automática