const { spawn } = require('child_process');
const path = require('path');

const serverScript = path.join(__dirname, 'dist', 'tool_code.js');
const child = spawn('node', [serverScript], {
  stdio: ['pipe', 'pipe', 'inherit'],
  env: { ...process.env, NODE_NO_WARNINGS: '1' }
});

let output = '';
child.stdout.on('data', (data) => {
  const str = data.toString();
  output += str;
  console.log('Received from stdout:', str);
  if (output.includes('\n')) {
    try {
      const lines = output.trim().split('\n');
      const lastLine = lines[lines.length - 1];
      const resp = JSON.parse(lastLine);
      console.log('Valid JSON received:', resp);
      if (resp.result && resp.result.protocolVersion) {
        console.log('Handshake successful!');
        child.kill();
        process.exit(0);
      }
    } catch (e) {
      console.error('Invalid JSON received yet or waiting for full line...');
    }
  }
});

const req = JSON.stringify({
  jsonrpc: "2.0",
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "test-client", version: "1.0.0" }
  },
  id: 1
}) + '\n';

console.log('Sending initialize request...');
child.stdin.write(req);

setTimeout(() => {
  console.log('Timeout reached. Output so far:', output);
  child.kill();
  process.exit(1);
}, 5000);
