import fs from "fs";
import path from "path";
import os from "os";
import { BIN_DIR, MODELS_DIR, DEFAULT_MODEL } from "./constants";
import { loadConfig } from "./config";

export function getBinPath(binName: string): string | null {
	const envPath = process.env.VOICE_PIPER_PATH;
	if (binName === "piper" && envPath && fs.existsSync(envPath)) {
		return envPath;
	}

	const system = os.platform();
	let fullBinName = binName;
	let subDir: string;

	if (system === "win32") {
		subDir = "windows";
		if (!fullBinName.endsWith(".exe")) fullBinName += ".exe";
	} else if (system === "linux") {
		subDir = "linux";
	} else {
		return null;
	}

	const binPath = path.join(BIN_DIR, subDir, fullBinName);
	return fs.existsSync(binPath) ? binPath : null;
}

export function getModelPath(): string | null {
	const envPath = process.env.VOICE_MODEL_PATH;
	if (envPath && fs.existsSync(envPath)) {
		return envPath;
	}

	const config = loadConfig();
	const modelVal = config.model || DEFAULT_MODEL;

	// 1. Try absolute path
	if (path.isAbsolute(modelVal) && fs.existsSync(modelVal)) {
		return modelVal;
	}

	const userModelDir = path.join(os.homedir(), ".voice", "models");
	const nameOnly = path.basename(modelVal);

	// 2. Try user's .voice/models directory FIRST (if not default)
	if (modelVal !== DEFAULT_MODEL) {
		const userPath = path.join(userModelDir, modelVal);
		if (fs.existsSync(userPath)) return userPath;
		
		const namePathUser = path.join(userModelDir, nameOnly);
		if (fs.existsSync(namePathUser)) return namePathUser;
	}

	// 3. Try extension's models directory
	const localPath = path.join(MODELS_DIR, modelVal);
	if (fs.existsSync(localPath)) return localPath;

	const namePathLocal = path.join(MODELS_DIR, nameOnly);
	if (fs.existsSync(namePathLocal)) return namePathLocal;

	// 4. Try user's .voice/models as a last resort even for default
	const userPathFallback = path.join(userModelDir, modelVal);
	if (fs.existsSync(userPathFallback)) return userPathFallback;

	// Fallback to default in local dir
	const fallbackDefault = path.join(MODELS_DIR, DEFAULT_MODEL);
	if (fs.existsSync(fallbackDefault)) {
		return fallbackDefault;
	}

	// Final search for any .onnx in local dir
	if (fs.existsSync(MODELS_DIR)) {
		const files = fs.readdirSync(MODELS_DIR);
		const onnxFile = files.find((f) => f.endsWith(".onnx"));
		if (onnxFile) {
			return path.join(MODELS_DIR, onnxFile);
		}
	}

	return null;
}
