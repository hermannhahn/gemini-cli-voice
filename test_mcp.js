const { spawn } = require('child_process');
const path = require('path');

const launcher = path.join(__dirname, 'launcher.js');
const child = spawn('node', [launcher], {
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
      const resp = JSON.parse(output.trim());
      console.log('Valid JSON received:', resp);
      console.log('Handshake successful!');
      child.kill();
      process.exit(0);
    } catch (e) {
      console.error('Invalid JSON received yet...');
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
