#!/usr/bin/env python
import json
import subprocess
import sys

# ruff: noqa: S607


def git_status() -> str:
    GREEN, YELLOW, RESET = '\033[32m', '\033[33m', '\033[0m'
    try:
        subprocess.check_output(['git', 'rev-parse', '--git-dir'], stderr=subprocess.DEVNULL)
        branch = subprocess.check_output(['git', 'branch', '--show-current'], text=True).strip()
        staged_output = subprocess.check_output(['git', 'diff', '--cached', '--numstat'], text=True).strip()
        modified_output = subprocess.check_output(['git', 'diff', '--numstat'], text=True).strip()
        staged = len(staged_output.split('\n')) if staged_output else 0
        modified = len(modified_output.split('\n')) if modified_output else 0

        git_status = branch
        if staged:
            git_status += f'{GREEN}+{staged}{RESET}'
        if modified:
            git_status += f'{YELLOW}~{modified}{RESET}'
    except:
        git_status = ''
    return git_status


def get_model(data: dict) -> str:
    if 'model' in data and 'display_name' in data['model']:
        return data['model']['display_name']
    return ''


def get_directory(data: dict) -> str:
    if 'workspace' in data and 'current_dir' in data['workspace']:
        return data['workspace']['current_dir']
    return ''


def get_context_window(data: dict) -> str:
    if 'context_window' in data and 'used_percentage' in data['context_window']:
        ctx = data['context_window']['used_percentage']
        if ctx:
            return f'ctx: {ctx}%'
    return ''


def get_rate_percentage(data: dict) -> str:
    if 'rate_limits' in data and 'five_hour' in data['rate_limits'] and 'used_percentage' in data['rate_limits']['five_hour']:
        rate = data['rate_limits']['five_hour']['used_percentage']
        if rate:
            return f'5h: {rate}%'
    return ''


data = json.load(sys.stdin)
model = get_model(data)
ctx = get_context_window(data)
rate = get_rate_percentage(data)
directory = get_directory(data)
status = git_status()
parts = []
if model:
    parts.append(model)
if ctx:
    parts.append(ctx)
if rate:
    parts.append(rate)
if directory:
    parts.append(directory)
if status:
    parts.append(status)

print(' | '.join(parts))
