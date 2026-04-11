const { spawnSync, execSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const isWin = os.platform() === 'win32';
const venvPath = path.join(__dirname, '.venv');

function findPython() {
  const candidates = isWin 
    ? [
        path.join(venvPath, 'Scripts', 'python.exe'), 
        path.join(venvPath, 'bin', 'python.exe'), 
        'python', 
        'py'
      ]
    : [path.join(venvPath, 'bin', 'python'), 'python3', 'python'];

  console.log(`Checking candidates: ${JSON.stringify(candidates)}`);

  for (const cmd of candidates) {
    try {
      console.log(`Trying: ${cmd}`);
      const res = spawnSync(cmd, ['--version'], { 
        shell: isWin && !path.isAbsolute(cmd),
        encoding: 'utf-8' 
      });
      console.log(`Status: ${res.status}, Error: ${res.error}`);
      
      if (res.status === 0) {
        if (isWin && !path.isAbsolute(cmd)) {
          try {
            // Use Get-Command for PowerShell
            const realPath = execSync(`powershell -c "(Get-Command ${cmd}).Source"`, { encoding: 'utf-8' }).trim();
            if (realPath && fs.existsSync(realPath)) return realPath;
          } catch (e) {
            console.log(`where ${cmd} failed: ${e.message}`);
          }
        }
        return cmd;
      }
    } catch (e) {
      console.log(`Failed to try ${cmd}: ${e.message}`);
    }
  }
  return isWin ? 'python' : 'python3';
}

const pythonCmd = findPython();
console.log(`Chosen Python: ${pythonCmd}`);
