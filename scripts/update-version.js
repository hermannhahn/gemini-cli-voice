const fs = require("fs");
const path = require("path");

// Get the new version from package.json
const packageJson = JSON.parse(
	fs.readFileSync(path.join(__dirname, "../package.json"), "utf8"),
);
const newVersion = packageJson.version;

console.log(`Updating other files to version ${newVersion}...`);

// Update gemini-extension.json
const geminiExtensionPath = path.join(__dirname, "../gemini-extension.json");
if (fs.existsSync(geminiExtensionPath)) {
	let content = fs.readFileSync(geminiExtensionPath, "utf8");
	content = content.replace(
		/"version":\s*".*?"/,
		`"version": "${newVersion}"`,
	);
	fs.writeFileSync(geminiExtensionPath, content);
	console.log("- gemini-extension.json updated.");
}

// Update pyproject.toml
const pyprojectPath = path.join(__dirname, "../pyproject.toml");
if (fs.existsSync(pyprojectPath)) {
	let content = fs.readFileSync(pyprojectPath, "utf8");
	content = content.replace(
		/^version\s*=\s*".*?"/m,
		`version = "${newVersion}"`,
	);
	fs.writeFileSync(pyprojectPath, content);
	console.log("- pyproject.toml updated.");
}

// Update src/gemini_voice/mcp.py
const mcpPath = path.join(__dirname, "../src/gemini_voice/mcp.py");
if (fs.existsSync(mcpPath)) {
	let content = fs.readFileSync(mcpPath, "utf8");
	content = content.replace(
		/^VERSION\s*=\s*".*?"/m,
		`VERSION = "${newVersion}"`,
	);
	fs.writeFileSync(mcpPath, content);
	console.log("- src/gemini_voice/mcp.py updated.");
}

// Update PKG-INFO if it exists
const pkgInfoPath = path.join(
	__dirname,
	"../src/gemini_cli_voice.egg-info/PKG-INFO",
);
if (fs.existsSync(pkgInfoPath)) {
	let content = fs.readFileSync(pkgInfoPath, "utf8");
	content = content.replace(/^Version:\s*.*$/m, `Version: ${newVersion}`);
	fs.writeFileSync(pkgInfoPath, content);
	console.log("- PKG-INFO updated.");
}
