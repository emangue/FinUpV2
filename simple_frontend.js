const express = require('express');
const app = express();
const port = process.env.PORT || 3080;

app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Finanças V4</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: system-ui, -apple-system, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 20px;
        }
        .container { 
            background: white; 
            padding: 40px; 
            border-radius: 16px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px; 
            width: 100%;
            text-align: center;
        }
        h1 { color: #2c3e50; margin-bottom: 10px; font-size: 2.5em; }
        .subtitle { color: #7f8c8d; margin-bottom: 30px; font-size: 1.1em; }
        .status { 
            background: #d5f4e6; 
            color: #16a085; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 20px 0;
            font-weight: bold;
        }
        .links { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 15px; 
            margin: 30px 0; 
        }
        .link { 
            background: #3498db; 
            color: white; 
            padding: 15px 20px; 
            text-decoration: none; 
            border-radius: 8px; 
            transition: all 0.3s;
            font-weight: 500;
            display: block;
        }
        .link:hover { background: #2980b9; transform: translateY(-2px); }
        .link.docs { background: #e74c3c; }
        .link.docs:hover { background: #c0392b; }
        .info { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0; 
            text-align: left;
            border-left: 4px solid #3498db;
        }
        .info h3 { color: #2c3e50; margin-bottom: 10px; }
        .info p { color: #5a6c7d; line-height: 1.6; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏦 Sistema de Finanças V4</h1>
        <p class="subtitle">Rodando nas portas corretas!</p>
        
        <div class="status">
            ✅ Sistema funcionando (Portas 8080 e 3080)
        </div>
        
        <div class="links">
            <a href="http://148.230.78.91:8080/api/health" class="link" target="_blank">Health Check</a>
            <a href="http://148.230.78.91:8080/docs" class="link docs" target="_blank">API Docs</a>
        </div>
        
        <div class="info">
            <h3>📊 Configuração Atual</h3>
            <p><strong>Frontend:</strong> Porta 3080 (esta página)</p>
            <p><strong>Backend:</strong> Porta 8080</p>
            <p><strong>Motivo:</strong> Portas 3000/8000 já ocupadas pelo Easypanel</p>
        </div>
        
        <div class="info">
            <h3>🌐 URLs de Acesso</h3>
            <p><a href="http://148.230.78.91:3080" target="_blank">http://148.230.78.91:3080</a> - Frontend</p>
            <p><a href="http://148.230.78.91:8080" target="_blank">http://148.230.78.91:8080</a> - Backend</p>
            <p><a href="http://148.230.78.91:8080/docs" target="_blank">http://148.230.78.91:8080/docs</a> - API Docs</p>
        </div>
    </div>
</body>
</html>
  `);
});

app.listen(port, '0.0.0.0', () => {
  console.log(\`Frontend rodando na porta \${port}\`);
});