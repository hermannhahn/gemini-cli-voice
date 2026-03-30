## Development Workflow

1. Change to `development` branch.
2. Modify any file you want.
3. Commit and push modifications to `development` branch.
4. Ask to user restart CLI for test.
5. After user inform the restart, test tool modifications.
6. If user ask to deploy, follow `Deploy Workflow` instructions.

## Deploy Workflow

1. Change to `development` branch.
2. Ensure `npm run update:version` was executed and changes are pushed.
    - This script will:
        - Run tests and lint.
        - (If pass) Update the version in all necessary files.
        - Commit and push changes.
3. Create Pull Request from `development` to `main` using `gh pr create` command.
4. Inform the user of the PR link for review and approval.
5. **WAIT** for the user to approve and merge the PR on GitHub.
6. If user ask to me accept and merge the PR, run `gh pr merge` command to merge the PR on GitHub.
7. After user confirmation of merge or if the PR is merged by me, run `npm run deploy` from the `development` branch.
    - This script will:
        - Change to `main` branch.
        - Run `git pull` (to fetch the merged PR).
        - Run Lint (extra check).
        - Create and Push Tag.
        - Create and Push Release on GitHub.
        - Update the local extension.
        - Return to `development` branch.
8. A - If get errors, go back to begin. (Item 1 of `Development Workflow`).
9. B - If don't get errors, at the end, the script will return to `development` branch.
10. Ask to user restart CLI for test.
11. After user inform the restart, test tool and check the modifications.
12. If user ask to deploy again, follow `Deploy Workflow` instructions.
