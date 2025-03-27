# CMPT 371 Project - Deny and Conquer

## Prerequisites

Ensure you have the following installed on your system:

- **[Python 3.11](https://www.python.org/downloads/)** (or the latest version)

## Local Installation

1. **Clone the repository**:

```sh
 git clone <repo-url>
```

Replace `<repo-url>` with the actual repository URL.

2. **Navigate to the root directory**:

```sh
cd <repo-name>
```

Replace `<repo-name>` with the cloned repository's directory name.

## Starting the Game

### Server Setup

One player must start the game server before others can join.

1. Open a terminal and navigate to the root directory of the game.
2. Run the following command:

```sh
python server.py
```

### Client Connection

All players (including the one who started the server) must run the client to join the
game.

1. Open a new terminal (can't be the same one the server was started on) and navigate to
   the game's root directory.
2. Run the following command:

```sh
python client.py
```
