import configparser
from typing import Optional
from pathlib import Path


class GitRepository:
    """
    A git repository
    """

    worktree: Path = None
    gitdir: Path = None
    conf: configparser.ConfigParser = None

    def __init__(self, path, force=False):
        self.worktree: Path = path
        self.gitdir: Path = path / '.git'

        if not (force or self.gitdir.is_dir()):
            raise Exception(f'Not a Git repository: {path}')

        # Read configuration file in .git/config
        self.conf = configparser.ConfigParser()
        cf: Path = repo_file(self, 'config')

        if cf and cf.exists():
            self.conf.read([cf])
        elif not force:
            raise Exception('Configuration file missing')

        if not force:
            vers = int(self.conf.get('core', 'repositoryformatversion'))
            if vers != 0 and not force:
                raise Exception(f'Unsupported repositoryformatversion {vers}')


def repo_path(repo: GitRepository, *path: str) -> Path:
    """
    Compute path under repo's gitdir.
    """
    return repo.gitdir.joinpath(*path)


def repo_file(repo: GitRepository, *path: str, mkdir: bool = False) -> Path:
    """
    Same as repo_path, but create dirname(*path) if absent.  For
    example, repo_file(r, \"refs\" \"remotes\", \"origin\", \"HEAD\") will create .git/refs/remotes/origin.
    """

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)


def repo_dir(repo: GitRepository, *path: str, mkdir: bool = False) -> Optional[Path]:
    """
    Same as repo_path, but mkdir *path if absent if mkdir.
    """

    path = repo_path(repo, *path)

    if path.exists():
        if path.is_dir():
            return path
        else:
            raise Exception(f'Not a directory {path}')

    if mkdir:
        path.mkdir(parents=True)
        return path
    else:
        return None


def repo_create(path: Path) -> GitRepository:
    """
    Create a new repository at path.
    """

    repo: GitRepository = GitRepository(path, True)

    if repo.worktree.exists():
        if not repo.worktree.is_dir():
            raise Exception(f'{path} is not a directory!')
        if [f for f in repo.worktree.glob('*')]:
            raise Exception(f'{path} is not empty!')
    else:
        repo.worktree.mkdir()

    assert (repo_dir(repo, "branches", mkdir=True))
    assert (repo_dir(repo, "objects", mkdir=True))
    assert (repo_dir(repo, "refs", "tags", mkdir=True))
    assert (repo_dir(repo, "refs", "heads", mkdir=True))

    # .git/description
    with repo_file(repo, "description").open(mode='w') as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    # .git/HEAD
    with repo_file(repo, "HEAD").open(mode='w') as f:
        f.write("ref: refs/heads/master\n")

    with repo_file(repo, "config").open(mode='w') as f:
        config = repo_default_config()
        config.write(f)

    return repo


def repo_default_config() -> configparser.ConfigParser:
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret


def repo_find(path: Path = Path.cwd(), required: bool = True) -> Optional[GitRepository]:
    if (path / '.git').is_dir():
        return GitRepository(path)

    parent = path.parent

    if parent == path:
        if required:
            raise Exception("No git directory.")
        else:
            return None

    # Recursive case
    return repo_find(parent, required)
