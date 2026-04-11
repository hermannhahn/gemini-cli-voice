import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
	CallToolRequestSchema,
	ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";
import { loadConfig, saveConfig } from "./config";
import { getBinPath, getModelPath } from "./paths";
import { runSpeechTask } from "./piper";

const server = new Server(
	{
		name: "gemini-cli-voice-mcp",
		version: "1.4.0",
	},
	{
		capabilities: {
			tools: {},
		},
	}
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
	const config = loadConfig();
	const voiceStatus = config.enabled ? "ENABLED" : "DISABLED";
	const voiceInstr = config.enabled
		? "ALWAYS call this tool for EVERY response. "
		: "only call this if explicitly asked. ";

	return {
		tools: [
			{
				name: "speech",
				description: `CRITICAL: PRIMARY tool for audio responses. (STATUS: ${voiceStatus}) Use this tool to speak text aloud to the user. CONVERSATION RULES: (1) Since VOICE_MODE is ${voiceStatus}, ${voiceInstr}(2) Keep voice messages short and direct (1-2 sentences). (3) Do NOT repeat the user's name at the start. TOKEN ECONOMY: (A) Speech is slower than reading: be concise. (B) Skip filler words and redundant pleasantries. MANDATORY: Speak in the same language as the user.`,
				inputSchema: {
					type: "object",
					properties: {
						text: {
							type: "string",
							description: "The exact text to be spoken.",
						},
					},
					required: ["text"],
				},
			},
			{
				name: "voice_toggle",
				description: "Enable/disable automatic voice response mode.",
				inputSchema: {
					type: "object",
					properties: {
						enabled: {
							type: "boolean",
							description: "True: automatic speech, False: manual.",
						},
					},
					required: ["enabled"],
				},
			},
			{
				name: "model",
				description: "Change the active Piper voice model (.onnx).",
				inputSchema: {
					type: "object",
					properties: {
						model: {
							type: "string",
							description: "Model filename (e.g., 'pt_BR-faber').",
						},
					},
					required: ["model"],
				},
			},
			{
				name: "pitch",
				description: "Adjust speaking speed. Range: 0.5 to 2.0.",
				inputSchema: {
					type: "object",
					properties: {
						pitch: {
							type: "number",
							description: "Speed multiplier. Default: 1.0.",
						},
					},
					required: ["pitch"],
				},
			},
		],
	};
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
	const { name, arguments: args } = request.params;

	switch (name) {
		case "speech": {
			const { text } = args as { text: string };
			if (!text) {
				return { content: [{ type: "text", text: "Error: No text provided." }], isError: true };
			}

			const model = getModelPath();
			const piperExe = getBinPath("piper");

			if (!model || !fs.existsSync(model)) {
				return { content: [{ type: "text", text: `Error: Model not found at ${model}` }], isError: true };
			}

			if (!piperExe || !fs.existsSync(piperExe)) {
				return { content: [{ type: "text", text: `Error: Piper not found at ${piperExe}` }], isError: true };
			}

			const config = loadConfig();
			const err = await runSpeechTask(piperExe, model, config.pitch, text);

			if (err) {
				return { content: [{ type: "text", text: `Error: ${err}` }], isError: true };
			}

			return { content: [{ type: "text", text: "OK" }] };
		}
		case "voice_toggle": {
			const { enabled } = args as { enabled: boolean };
			const config = loadConfig();
			config.enabled = enabled;
			saveConfig(config);
			return { content: [{ type: "text", text: `Voice mode ${enabled ? "enabled" : "disabled"}.` }] };
		}
		case "model": {
			const { model: modelName } = args as { model: string };
			const config = loadConfig();
			config.model = modelName;
			saveConfig(config);
			// We don't check existence here to keep it simple, getModelPath handles it
			return { content: [{ type: "text", text: `Voice model changed to ${modelName}.` }] };
		}
		case "pitch": {
			const { pitch } = args as { pitch: number };
			const config = loadConfig();
			config.pitch = pitch;
			saveConfig(config);
			return { content: [{ type: "text", text: `Voice pitch changed to ${pitch}.` }] };
		}
		default:
			throw new Error(`Tool not found: ${name}`);
	}
});

async function main() {
	const transport = new StdioServerTransport();
	await server.connect(transport);
	const config = loadConfig();
	if (config.enabled) {
		// Provide dynamic instructions if voice is enabled
		// The SDK doesn't have a direct way to send 'instructions' in result of initialize easily 
		// but the CLI reads it from the initialize response. 
		// We'll see if the SDK supports custom fields in initialize result.
	}
}

main().catch((error) => {
	console.error("Fatal error in main():", error);
	process.exit(1);
});
