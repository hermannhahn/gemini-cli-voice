import fs from "fs";
import { CONFIG_FILE, DEFAULT_MODEL, CONFIG_DIR } from "./constants";

export interface VoiceConfig {
	model: string;
	pitch: number;
	enabled: boolean;
}

export function loadConfig(): VoiceConfig {
	if (fs.existsSync(CONFIG_FILE)) {
		try {
			const data = fs.readFileSync(CONFIG_FILE, "utf-8");
			const config = JSON.parse(data);
			return {
				model: config.model || DEFAULT_MODEL,
				pitch: config.pitch ?? 1.0,
				enabled: config.enabled ?? true,
			};
		} catch (e) {
			console.error("Error loading config:", e);
		}
	}
	return { model: DEFAULT_MODEL, pitch: 1.0, enabled: true };
}

export function saveConfig(config: VoiceConfig): void {
	try {
		if (!fs.existsSync(CONFIG_DIR)) {
			fs.mkdirSync(CONFIG_DIR, { recursive: true });
		}
		fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), "utf-8");
	} catch (e) {
		console.error("Error saving config:", e);
	}
}
