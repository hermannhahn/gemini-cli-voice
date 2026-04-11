const { spawn } = require('child_process');
const path = require('path');

const launcher = path.join(__dirname, 'launcher.cjs');
const child = spawn('node', ['--no-warnings', launcher], {
  stdio: ['pipe', 'pipe', 'inherit']
});

let output = '';
child.stdout.on('data', (data) => {
  output += data.toString();
  console.log('Received:', data.toString());
  if (output.includes('\n')) {
    console.log('Got a full line! Handshake successful.');
    process.exit(0);
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
  console.log('Timeout reached. No response.');
  process.exit(1);
}, 5000);
