export default {
  '*.{json,md,yaml}': (stagedFiles) =>
    `prettier --write ${stagedFiles.join(' ')}`,

  '(*.{py,pyi}|pyproject.toml)': (stagedFiles) => [
    'pyright .',
    'ruff check --fix .',
    `ruff format --force-exclude ${stagedFiles.join(' ')}`,
  ],
};
