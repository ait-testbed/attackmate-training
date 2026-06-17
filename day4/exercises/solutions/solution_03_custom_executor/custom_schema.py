# Solution for Exercise 4: HelloCommand schema
#
# Copy to: src/attackmate/schemas/hello.py

from typing import Literal
from attackmate.schemas.base import BaseCommand
from attackmate.command import CommandRegistry


@CommandRegistry.register('hello')
class HelloCommand(BaseCommand):
    type: Literal['hello']
    cmd: str = ''       # BaseCommand requires cmd; override with a default since hello doesn't use it
    message: str = 'Hello, AttackMate!'
