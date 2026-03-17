const { spawn, execSync } = require('child_process');
const pkg = require('../package.json');

const geminiDeps = pkg['gemini-dependencies'] || {};
const depNames = Object.keys(geminiDeps);

if (depNames.length > 0) {
    try {
        console.log('Verificando extensões instaladas...');
        const listOutput = execSync('gemini extensions list -o json').toString();
        const start = listOutput.indexOf('[');
        const installedList = start !== -1 ? JSON.parse(listOutput.slice(start)) : [];
        const installedNames = installedList.map(ext => ext.name);

        for (const name of depNames) {
            if (!installedNames.includes(name)) {
                const url = geminiDeps[name];
                console.log(`Instalando extensão ausente: ${name} de ${url}...`);
                execSync(`gemini extensions install ${url}`, { stdio: 'inherit' });
            }
        }
    } catch (error) {
        console.error('Erro ao verificar/instalar extensões:', error.message);
    }
}

const depsString = depNames.join(',');
console.log(`Iniciando tmux com as extensões: ${depsString || 'nenhuma'}`);

// Inicia o tmux com a flag -e do gemini
const tmux = spawn('tmux', ['new', '-s', 'gemini-cli', `gemini -e ${depsString}`], {
    stdio: 'inherit'
});

tmux.on('exit', (code) => {
    process.exit(code);
});
