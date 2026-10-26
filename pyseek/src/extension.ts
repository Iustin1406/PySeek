import * as vscode from 'vscode';


interface SearchResult {
    function_name: string;
    filepath: string;
    scope: string[];
    start_line: number;
    score: number;
}


export function activate(context: vscode.ExtensionContext) {

    console.log('PySeek extension is active');

    const searchCommand = vscode.commands.registerCommand(
        'pyseek.searchCode',
        async () => {

            const query = await vscode.window.showInputBox({
                prompt: 'Search code with PySeek'
            });

            if (query === undefined || query.trim() === '') {
                return;
            }

            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];

            if (workspaceFolder === undefined) {
                vscode.window.showErrorMessage(
                    'No repository is currently open'
                );
                return;
            }

            const repositoryPath = workspaceFolder.uri.fsPath;

            const serverUrl = vscode.workspace
                .getConfiguration('pyseek')
                .get<string>(
                    'serverUrl',
                    'http://127.0.0.1:8000'
                );

            const params = new URLSearchParams({
                query: query,
                repository_path: repositoryPath
            });

            try {
                const response = await fetch(
                    `${serverUrl}/search?${params.toString()}`
                );

                if (!response.ok) {
                    vscode.window.showErrorMessage(
                        `PySeek search failed: ${response.status}`
                    );
                    return;
                }

                const results =
                    await response.json() as SearchResult[];

                if (results.length === 0) {
                    vscode.window.showInformationMessage(
                        'No results found. The repository may not be indexed.'
                    );
                    return;
                }

                const items = results.map(result => ({
                    label: result.function_name,
                    description: result.filepath,
                    detail:
                        `Score: ${result.score.toFixed(3)} | ` +
                        `Scope: ${result.scope.join(' -> ')}`,
                    result: result
                }));

                const selected = await vscode.window.showQuickPick(
                    items,
                    {
                        placeHolder: 'Select a search result'
                    }
                );

                if (selected === undefined) {
                    return;
                }

                const fileUri = vscode.Uri.file(
                    selected.result.filepath
                );

                const document =
                    await vscode.workspace.openTextDocument(fileUri);

                const editor =
                    await vscode.window.showTextDocument(document);

                const line = selected.result.start_line - 1;

                const position = new vscode.Position(
                    line,
                    0
                );

                editor.selection = new vscode.Selection(
                    position,
                    position
                );

                editor.revealRange(
                    new vscode.Range(position, position),
                    vscode.TextEditorRevealType.InCenter
                );

            } catch (error) {
                vscode.window.showErrorMessage(
                    'Could not connect to PySeek server'
                );
            }
        }
    );


    const indexCommand = vscode.commands.registerCommand(
        'pyseek.indexRepository',
        async () => {

            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];

            if (workspaceFolder === undefined) {
                vscode.window.showErrorMessage(
                    'No repository is currently open'
                );
                return;
            }

            const repositoryPath = workspaceFolder.uri.fsPath;

            const serverUrl = vscode.workspace
                .getConfiguration('pyseek')
                .get<string>(
                    'serverUrl',
                    'http://127.0.0.1:8000'
                );

            try {
                await vscode.window.withProgress(
                    {
                        location: vscode.ProgressLocation.Notification,
                        title: 'Indexing repository...',
                        cancellable: false
                    },
                    async () => {

                        const response = await fetch(
                            `${serverUrl}/index`,
                            {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    repository_path: repositoryPath
                                })
                            }
                        );

                        if (!response.ok) {
                            throw new Error(
                                `Indexing failed: ${response.status}`
                            );
                        }
                    }
                );

                vscode.window.showInformationMessage(
                    'Repository indexed successfully'
                );

            } catch (error) {
                if (error instanceof Error &&
                    error.message.startsWith('Indexing failed')) {

                    vscode.window.showErrorMessage(error.message);
                    return;
                }

                vscode.window.showErrorMessage(
                    'Could not connect to PySeek server'
                );
            }
        }
    );


    context.subscriptions.push(
        searchCommand,
        indexCommand
    );
}


export function deactivate() {}