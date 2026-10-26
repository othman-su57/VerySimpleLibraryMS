# Library System

A simple library management system built with **C# and .NET 10** as a training project after learning C#.

The project focuses on practicing object-oriented programming, domain modeling, and basic software design through a practical example.

## Features

- Manage books and their physical copies.
- Assign a unique identifier to each book copy.
- Track copy availability.
- Borrow available copies and return borrowed ones.
- Store inventory data in memory.
- Test inventory behavior under repeated operations and randomized workloads.

## Project Structure

The solution is organized into separate projects:

```text
LibrarySystem/
──── src/
    ├── Library.Domain/
    └── Library.Console/
```

- **Library.Domain** — Core domain entities and inventory rules.
- **Library.Application** — Application services and abstractions.
- **Library.Infrastructure** — Data storage and infrastructure implementations.
- **Library.Console** — Console application used to run and experiment with the system.
- **Library.Tests** — Project for automated tests.

## Domain Model

The current model distinguishes between a book title and its physical copies.

- **Book** represents a book title.
- **BookCopy** represents an individual physical copy and has a unique identifier.
- **Inventory** manages registered titles and their copies.

Each copy has one of two states:

- `Available` — The copy can be borrowed.
- `Borrowed` — The copy is currently borrowed.

Borrowing and returning a copy change its state, while the domain model is responsible for enforcing the corresponding rules.

## Getting Started

### Requirements

- [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0)

### Run the Application

Clone the repository:

```bash
git clone https://github.com/othman-su57/VerySimpleLibraryMS.git
cd VerySimpleLibraryMS
```

Build the solution:

```bash
dotnet build
```

Run the console application:

```bash
dotnet run --project src/Library.Console
```






## Current Limitations

This is a learning project, so its scope is intentionally limited.

- Inventory data is stored in memory and is not persisted between application runs.
- There is no user or member management.
- Borrowing does not yet include due dates or borrowing history.
- The project does not attempt to model every real-world library workflow.

These limitations can be addressed as the project evolves and new requirements emerge.

## Goals

The main goal is to apply C# concepts in a working project while exploring:

- Object-oriented programming and encapsulation.
- Domain modeling and business rules.
- Separation of concerns between application layers.
- Interfaces and dependency boundaries.
- Testing and verification of program behavior.

## Status

**Work in progress.** This project is being developed incrementally as a way to practice C# and improve software design skills.
