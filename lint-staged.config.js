export default {
  '*.{json,md,yaml}': (stagedFiles) =>
    `prettier --write ${stagedFiles.join(' ')}`,

  '*.py': (stagedFiles) => [
    'pyright .',
    'ruff check --fix .',
    `ruff format --force-exclude ${stagedFiles.join(' ')}`,
  ],
};
