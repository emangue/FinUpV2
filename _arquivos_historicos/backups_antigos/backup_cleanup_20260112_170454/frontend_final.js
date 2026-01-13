const express = require('express');
const app = express();
const port = process.env.PORT || 3080;

app.get('/', (req, res) => {
  const html = `<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Financas V4</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 20px; }
        .status { text-align: center; margin: 30px 0; color: #27ae60; font-weight: bold; font-size: 18px; }
        .links { display: flex; justify-content: center; gap: 20px; margin: 30px 0; }
        .link { background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }
        .link:hover { background: #2980b9; }
        .info { background: #ecf0f1; padding: 20px; border-radius: 6px; margin: 20px 0; }
        .info h3 { color: #2c3e50; margin-bottom: 10px; }
        .info p { color: #5a6c7d; line-height: 1.6; margin: 8px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏦 Sistema de Financas V4</h1>
        <div class="status">✅ Sistema funcionando (Portas 8080 e 3080)</div>
        
        <div class="links">
            <a href="http://148.230.78.91:8080/api/health" class="link" target="_blank">Health Check</a>
            <a href="http://148.230.78.91:8080/docs" class="link" target="_blank">API Docs</a>
        </div>
        
        <div class="info">
            <h3>📊 Configuracao Atual</h3>
            <p><strong>Frontend:</strong> Porta 3080 (esta pagina)</p>
            <p><strong>Backend:</strong> Porta 8080</p>
            <p><strong>Motivo:</strong> Portas 3000/8000 ja ocupadas pelo Easypanel</p>
        </div>
        
        <div class="info">
            <h3>🌐 URLs de Acesso</h3>
            <p><a href="http://148.230.78.91:3080" target="_blank">Frontend: http://148.230.78.91:3080</a></p>
            <p><a href="http://148.230.78.91:8080" target="_blank">Backend: http://148.230.78.91:8080</a></p>
            <p><a href="http://148.230.78.91:8080/docs" target="_blank">API Docs: http://148.230.78.91:8080/docs</a></p>
        </div>
    </div>
</body>
</html>`;
  
  res.send(html);
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'frontend_ok', backend: 'http://148.230.78.91:8080' });
});

app.listen(port, '0.0.0.0', () => {
  console.log('Frontend rodando na porta ' + port);
});

console.log('Iniciando servidor Express na porta ' + (process.env.PORT || 3080));