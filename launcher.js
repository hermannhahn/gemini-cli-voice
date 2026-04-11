const { spawn, spawnSync, execSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const isWin = os.platform() === 'win32';

/**
 * Procura pelo executável do Python de forma resiliente.
 */
function findPython() {
  const venvPath = path.join(__dirname, '.venv');
  const candidates = isWin 
    ? [
        path.join(venvPath, 'Scripts', 'python.exe'), 
        path.join(venvPath, 'bin', 'python.exe'), 
        'python', 
        'py'
      ]
    : [path.join(venvPath, 'bin', 'python'), 'python3', 'python'];

  for (const cmd of candidates) {
    try {
      const res = spawnSync(cmd, ['--version'], { shell: false });
      if (res.status === 0) {
        if (isWin && !path.isAbsolute(cmd)) {
          try {
            const realPath = execSync(`where ${cmd}`, { encoding: 'utf-8' }).split('\r\n')[0].trim();
            if (realPath && fs.existsSync(realPath)) return realPath;
          } catch (e) {}
        }
        return cmd;
      }
    } catch (e) {}
  }
  return isWin ? 'python' : 'python3';
}

const pythonCmd = findPython();
const scriptPath = path.resolve(__dirname, 'tool_code.py');

// Spawna o processo MCP. 
// Usamos pipe manual para ter certeza que nada (como warnings) suje o stdout.
const child = spawn(pythonCmd, [scriptPath, ...process.argv.slice(2)], {
  stdio: ['pipe', 'pipe', 'pipe'],
  shell: isWin && !path.isAbsolute(pythonCmd),
  env: { ...process.env, PYTHONUTF8: '1' }
});

// Proxy stdin/stdout
process.stdin.pipe(child.stdin);
child.stdout.pipe(process.stdout);

// Redireciona stderr para o console.error do Node, que não deve afetar o stdout do processo pai
child.stderr.on('data', (data) => {
  process.stderr.write(`[Python Stderr]: ${data}`);
});

child.on('exit', (code) => {
  if (code !== 0) {
    process.stderr.write(`[Python Exit]: Child exited with code ${code}\n`);
  }
  process.exit(code || 0);
});

child.on('error', (err) => {
  process.stderr.write(`[Spawn Error]: ${err.message}\n`);
  process.exit(1);
});
