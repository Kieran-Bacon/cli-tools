import os
import stow
import argparse

parser = argparse.ArgumentParser('Linker')

parser.add_argument('project', default=None, help='Path to project that is to be linked')

args = parser.parse_args()


# Path to projects
projects = r'C:\Users\kieran\Projects'

settings = stow.join(stow.dirname(stow.abspath(__file__)), 'devcontainer.json')

def linkProject(project: stow.Directory):

    path = stow.abspath(stow.join(project, '.devcontainer', 'devcontainer.json'))

    print(f'mklink {path} {settings}')
    # continue

    if stow.exists(path):
        stow.rm(path)

    os.system(f'mklink {path} {settings}')


if args.project is not None:

    project = stow.artefact(args.project)

    if isinstance(project, stow.Directory):
        linkProject(project)

    else:
        raise ValueError('Path does not lead to a directory')

else:
    # Link all

    ignoreDirectories = ['Personal', 'settings']

    for artefact in stow.ls(projects):
        if isinstance(artefact, stow.Directory) and artefact.name not in ignoreDirectories:
            for subArtefact in stow.ls(artefact):
                linkProject(subArtefact)