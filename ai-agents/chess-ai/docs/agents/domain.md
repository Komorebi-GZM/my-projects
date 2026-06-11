# Domain Vocabulary

Key terms and concepts for the chess_ai project.

## Core Domain Terms

| Term | Definition |
|------|------------|
| **Piece** | A single chess piece (King, Advisor, Elephant, Horse, Chariot, Cannon, Soldier) |
| **Board** | 10x9 grid representing the Xiangqi board |
| **Position** | A location on the board, typically (row, col) where row 0 is black back rank |
| **Move** | An action that moves a piece from one position to another |
| **Side** | Either "red" or "black" - the two players |
| **FEN** | Forsyth-Edwards Notation - string representation of board state |

## Game States

| State | Definition |
|-------|------------|
| **Playing** | Game in progress |
| **Check** | King under attack |
| **Checkmate** | King has no legal moves while in check |
| **Stalemate** | No legal moves but not in check |
| **Resign** | Player concedes |
| **Draw** | Game ends in tie |

## AI Terms

| Term | Definition |
|------|------------|
| **Agent** | LangGraph state machine that generates moves |
| **Orchestrator** | Entry point that manages agent workflow |
| **Difficulty** | AI behavior setting (Easy/Medium/Hard) via LLM temperature |
| **Temperature** | LLM sampling parameter - higher = more random |
| **Checkpoint** | Saved agent state for recovery |
| **Retry** | Agent attempt to generate valid move |

## Configuration Terms

| Term | Definition |
|------|------------|
| **ConfigManager** | Singleton managing YAML + env var configuration |
| **Defaults** | Hardcoded configuration values |
| **Persistence** | Saving/loading config to YAML file |

## Architecture Layers

```
GUI (Pygame)
    ↓
Rule Engine (board, move, rules)
    ↓
Agent (LangGraph state machine)
    ↓
LLM Client (API abstraction)
    ↓
Infrastructure (config, storage, logging)
```

## Layer Isolation Rules

- Upper layers MUST NOT directly call lower layers
- GUI ↔ Agent only (via controller)
- Agent ↔ LLM Client only (via nodes)
- ConfigManager accessed by any layer that needs configuration