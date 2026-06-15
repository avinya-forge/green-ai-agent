import * as vscode from 'vscode';
import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind,
    Executable
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('Green AI extension is now active!');

    const config = vscode.workspace.getConfiguration('green-ai');
    const isEnabled = config.get<boolean>('enable', true);

    if (!isEnabled) {
        console.log('Green AI is disabled in settings.');
        return;
    }

    const serverPath = config.get<string>('scanner.serverPath', 'green-ai');

    // We launch green-ai lsp on stdio
    const runArgs: string[] = ['lsp'];
    const debugArgs: string[] = ['lsp'];

    const serverExecutable: Executable = {
        command: serverPath || 'green-ai',
        args: runArgs,
        options: { env: process.env }
    };

    const serverOptions: ServerOptions = {
        run: serverExecutable,
        debug: serverExecutable
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: 'file', language: 'python' },
            { scheme: 'file', language: 'javascript' },
            { scheme: 'file', language: 'typescript' },
            { scheme: 'file', language: 'java' },
            { scheme: 'file', language: 'go' },
        ],
        synchronize: {
            // Notify the server about file changes to '.green-ai.yaml'
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.green-ai.yaml')
        }
    };

    client = new LanguageClient(
        'greenAI',
        'Green AI Language Server',
        serverOptions,
        clientOptions
    );

    client.start();

    let disposable = vscode.commands.registerCommand('green-ai.scan', () => {
        vscode.window.showInformationMessage('Green AI: Scanning file...');
        // We could send a custom request to LSP here
    });

    context.subscriptions.push(disposable);
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
