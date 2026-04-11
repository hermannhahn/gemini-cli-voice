const { spawn, spawnSync, execSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const isWin = os.platform() === 'win32';
const logFile = path.join(__dirname, 'launcher.log');

function log(msg) {
  const timestamp = new Date().toISOString();
  fs.appendFileSync(logFile, `[${timestamp}] ${msg}\n`);
}

/**
 * Procura pelo executável do Python de forma resiliente.
 */
function findPython() {
  const venvPath = path.join(__dirname, '.venv');
  const candidates = isWin 
    ? [
        path.join(venvPath, 'Scripts', 'python.exe'), 
        path.join(venvPath, 'bin', 'python.exe'), 
        path.join(venvPath, 'bin', 'python'),
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
            const whereRes = execSync(`where ${cmd}`, { encoding: 'utf-8' });
            const realPath = whereRes.split(/\r?\n/)[0].trim();
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

log(`Starting: ${pythonCmd} ${scriptPath}`);

const child = spawn(pythonCmd, [scriptPath, ...process.argv.slice(2)], {
  stdio: ['pipe', 'pipe', 'inherit'],
  shell: false,
  env: { 
    ...process.env, 
    PYTHONUTF8: '1',
    NODE_NO_WARNINGS: '1'
  }
});

// Proxy stdin/stdout
process.stdin.pipe(child.stdin);
child.stdout.pipe(process.stdout);

child.on('exit', (code) => {
  log(`Child exited with code ${code}`);
  process.exit(code || 0);
});

child.on('error', (err) => {
  log(`Spawn error: ${err.message}`);
  process.stderr.write(`[Launcher Error]: ${err.message}\n`);
  process.exit(1);
});

process.stdin.on('error', (err) => {
  log(`Stdin error: ${err.message}`);
});

process.stdout.on('error', (err) => {
  log(`Stdout error: ${err.message}`);
});
