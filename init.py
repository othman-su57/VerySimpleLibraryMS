import os, textwrap, zipfile

root = "/mnt/data/LibrarySystem"
files = {
"LibrarySystem.sln": """Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Domain", "src\\Library.Domain\\Library.Domain.csproj", "{A1111111-1111-4111-8111-111111111111}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Application", "src\\Library.Application\\Library.Application.csproj", "{A2222222-2222-4222-8222-222222222222}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Infrastructure", "src\\Library.Infrastructure\\Library.Infrastructure.csproj", "{A3333333-3333-4333-8333-333333333333}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Console", "src\\Library.Console\\Library.Console.csproj", "{A4444444-4444-4444-8444-444444444444}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Tests", "tests\\Library.Tests\\Library.Tests.csproj", "{A5555555-5555-4555-8555-555555555555}"
EndProject
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
        Debug|Any CPU = Debug|Any CPU
        Release|Any CPU = Release|Any CPU
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
        {A1111111-1111-4111-8111-111111111111}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A1111111-1111-4111-8111-111111111111}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A1111111-1111-4111-8111-111111111111}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A1111111-1111-4111-8111-111111111111}.Release|Any CPU.Build.0 = Release|Any CPU
        {A2222222-2222-4222-8222-222222222222}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A2222222-2222-4222-8222-222222222222}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A2222222-2222-4222-8222-222222222222}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A2222222-2222-4222-8222-222222222222}.Release|Any CPU.Build.0 = Release|Any CPU
        {A3333333-3333-4333-8333-333333333333}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A3333333-3333-4333-8333-333333333333}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A3333333-3333-4333-8333-333333333333}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A3333333-3333-4333-8333-333333333333}.Release|Any CPU.Build.0 = Release|Any CPU
        {A4444444-4444-4444-8444-444444444444}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A4444444-4444-4444-8444-444444444444}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A4444444-4444-4444-8444-444444444444}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A5555555-5555-4555-8555-555555555555}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A5555555-5555-4555-8555-555555555555}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A5555555-5555-4555-8555-555555555555}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A5555555-5555-4555-8555-555555555555}.Release|Any CPU.Build.0 = Release|Any CPU
    EndGlobalSection
EndGlobal
""",
"Directory.Build.props": """<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>
</Project>
""",
"README.md": """# LibrarySystem

Small library inventory project scaffold in C#/.NET.

## Projects
- `Library.Domain`: domain entities and inventory invariants; no I/O dependencies.
- `Library.Application`: application use cases and repository contracts.
- `Library.Infrastructure`: in-memory persistence adapter for the initial scaffold.
- `Library.Console`: composition root / command-line entry point.
- `Library.Tests`: unit tests for domain behavior.

## Run
```bash
dotnet restore
dotnet build
dotnet test
dotnet run --project src/Library.Console
```

## Initial design decisions
- `Book` represents a bibliographic title.
- `BookCopy` represents one physical copy.
- `Inventory` is the in-memory authority for creating books and copies.
- `Book` and `BookCopy` constructors are `internal` to discourage creation outside the domain assembly. This is an assembly-level restriction, not a security boundary.
- This scaffold intentionally uses in-memory storage. Add SQLite/database I/O behind the application repository interfaces later.
- A production database must enforce concurrency-sensitive invariants too; an in-memory dictionary alone cannot protect multiple processes or application instances.
""",
"src/Library.Domain/Library.Domain.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>Library.Domain</AssemblyName>
    <RootNamespace>Library.Domain</RootNamespace>
  </PropertyGroup>
</Project>
""",
"src/Library.Domain/Entities/Book.cs": """namespace Library.Domain.Entities;

public sealed class Book
{
    public int Id { get; }
    public string Name { get; }

    internal Book(int id, string name)
    {
        if (id <= 0)
            throw new ArgumentOutOfRangeException(nameof(id), "Book ID must be positive.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Book name cannot be empty.", nameof(name));

        Id = id;
        Name = name.Trim();
    }
}
""",
"src/Library.Domain/Entities/BookCopy.cs": """namespace Library.Domain.Entities;

public enum BookCopyStatus
{
    Available,
    Borrowed,
    Maintenance,
    Lost
}

public sealed class BookCopy
{
    public int Id { get; }
    public Book Book { get; }
    public BookCopyStatus Status { get; private set; }

    internal BookCopy(int id, Book book)
    {
        if (id <= 0)
            throw new ArgumentOutOfRangeException(nameof(id));

        ArgumentNullException.ThrowIfNull(book);

        Id = id;
        Book = book;
        Status = BookCopyStatus.Available;
    }

    public void MarkBorrowed()
    {
        if (Status != BookCopyStatus.Available)
            throw new InvalidOperationException("Only available copies can be borrowed.");

        Status = BookCopyStatus.Borrowed;
    }

    public void MarkReturned()
    {
        if (Status != BookCopyStatus.Borrowed)
            throw new InvalidOperationException("Only borrowed copies can be returned.");

        Status = BookCopyStatus.Available;
    }
}
""",
"src/Library.Domain/Inventory/Inventory.cs": """using Library.Domain.Entities;

namespace Library.Domain.Inventory;

public sealed class Inventory
{
    private readonly Dictionary<int, Book> _books = new();
    private readonly Dictionary<int, BookCopy> _copies = new();

    public IReadOnlyCollection<Book> Books => _books.Values;
    public IReadOnlyCollection<BookCopy> Copies => _copies.Values;

    public Book AddBook(int id, string name)
    {
        if (_books.ContainsKey(id))
            throw new InvalidOperationException($"A book with ID {id} already exists.");

        var book = new Book(id, name);
        _books.Add(id, book);
        return book;
    }

    public Book GetBook(int bookId)
    {
        if (!_books.TryGetValue(bookId, out var book))
            throw new KeyNotFoundException($"Book {bookId} was not found.");

        return book;
    }

    public BookCopy AddCopy(int copyId, int bookId)
    {
        if (_copies.ContainsKey(copyId))
            throw new InvalidOperationException($"A copy with ID {copyId} already exists.");

        var book = GetBook(bookId);
        var copy = new BookCopy(copyId, book);
        _copies.Add(copyId, copy);
        return copy;
    }

    public BookCopy GetCopy(int copyId)
    {
        if (!_copies.TryGetValue(copyId, out var copy))
            throw new KeyNotFoundException($"Copy {copyId} was not found.");

        return copy;
    }
}
""",
"src/Library.Application/Library.Application.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>Library.Application</AssemblyName>
    <RootNamespace>Library.Application</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Library.Domain/Library.Domain.csproj" />
  </ItemGroup>
</Project>
""",
"src/Library.Application/Abstractions/IInventoryRepository.cs": """using Library.Domain.Entities;

namespace Library.Application.Abstractions;

/// <summary>
/// Persistence contract. Implementations can use SQLite, PostgreSQL, or another store.
/// </summary>
public interface IInventoryRepository
{
    Task<IReadOnlyList<BookRecord>> LoadBooksAsync(CancellationToken cancellationToken = default);
    Task<IReadOnlyList<BookCopyRecord>> LoadCopiesAsync(CancellationToken cancellationToken = default);
    Task SaveBookAsync(BookRecord book, CancellationToken cancellationToken = default);
    Task SaveCopyAsync(BookCopyRecord copy, CancellationToken cancellationToken = default);
}

public sealed record BookRecord(int Id, string Name);
public sealed record BookCopyRecord(int Id, int BookId, BookCopyStatus Status);
""",
"src/Library.Application/Services/LibraryService.cs": """using Library.Application.Abstractions;
using Library.Domain.Entities;
using Library.Domain.Inventory;

namespace Library.Application.Services;

public sealed class LibraryService
{
    private readonly Inventory _inventory;
    private readonly IInventoryRepository _repository;

    public LibraryService(Inventory inventory, IInventoryRepository repository)
    {
        _inventory = inventory;
        _repository = repository;
    }

    public async Task<Book> AddBookAsync(int id, string name, CancellationToken cancellationToken = default)
    {
        var book = _inventory.AddBook(id, name);
        await _repository.SaveBookAsync(new BookRecord(book.Id, book.Name), cancellationToken);
        return book;
    }

    public async Task<BookCopy> AddCopyAsync(int copyId, int bookId, CancellationToken cancellationToken = default)
    {
        var copy = _inventory.AddCopy(copyId, bookId);
        await _repository.SaveCopyAsync(
            new BookCopyRecord(copy.Id, copy.Book.Id, copy.Status), cancellationToken);
        return copy;
    }

    public Book GetBook(int id) => _inventory.GetBook(id);

    public BookCopy GetCopy(int id) => _inventory.GetCopy(id);
}
""",
"src/Library.Infrastructure/Library.Infrastructure.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>Library.Infrastructure</AssemblyName>
    <RootNamespace>Library.Infrastructure</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Library.Domain/Library.Domain.csproj" />
    <ProjectReference Include="../Library.Application/Library.Application.csproj" />
  </ItemGroup>
</Project>
""",
"src/Library.Infrastructure/Persistence/InMemoryInventoryRepository.cs": """using Library.Application.Abstractions;
using Library.Domain.Entities;

namespace Library.Infrastructure.Persistence;

/// <summary>
/// Temporary adapter: data is lost when the process exits.
/// Replace with a database-backed implementation later.
/// </summary>
public sealed class InMemoryInventoryRepository : IInventoryRepository
{
    private readonly Dictionary<int, BookRecord> _books = new();
    private readonly Dictionary<int, BookCopyRecord> _copies = new();

    public Task<IReadOnlyList<BookRecord>> LoadBooksAsync(CancellationToken cancellationToken = default)
        => Task.FromResult<IReadOnlyList<BookRecord>>(_books.Values.ToArray());

    public Task<IReadOnlyList<BookCopyRecord>> LoadCopiesAsync(CancellationToken cancellationToken = default)
        => Task.FromResult<IReadOnlyList<BookCopyRecord>>(_copies.Values.ToArray());

    public Task SaveBookAsync(BookRecord book, CancellationToken cancellationToken = default)
    {
        if (!_books.TryAdd(book.Id, book))
            throw new InvalidOperationException($"Book {book.Id} already exists in storage.");

        return Task.CompletedTask;
    }

    public Task SaveCopyAsync(BookCopyRecord copy, CancellationToken cancellationToken = default)
    {
        if (!_books.ContainsKey(copy.BookId))
            throw new KeyNotFoundException($"Book {copy.BookId} does not exist in storage.");

        if (!_copies.TryAdd(copy.Id, copy))
            throw new InvalidOperationException($"Copy {copy.Id} already exists in storage.");

        return Task.CompletedTask;
    }
}
""",
"src/Library.Infrastructure/InventoryLoader.cs": """using Library.Application.Abstractions;
using Library.Domain.Inventory;

namespace Library.Infrastructure;

/// <summary>
/// Loads stored records into the in-memory domain inventory at startup.
/// </summary>
public sealed class InventoryLoader
{
    private readonly IInventoryRepository _repository;

    public InventoryLoader(IInventoryRepository repository) => _repository = repository;

    public async Task<Inventory> LoadAsync(CancellationToken cancellationToken = default)
    {
        var inventory = new Inventory();
        var books = await _repository.LoadBooksAsync(cancellationToken);
        var copies = await _repository.LoadCopiesAsync(cancellationToken);

        foreach (var book in books)
            inventory.AddBook(book.Id, book.Name);

        foreach (var copy in copies)
        {
            var loadedCopy = inventory.AddCopy(copy.Id, copy.BookId);
            // Restore persisted status through domain behavior rather than public setters.
            if (copy.Status == Library.Domain.Entities.BookCopyStatus.Borrowed)
                loadedCopy.MarkBorrowed();
        }

        return inventory;
    }
}
""",
"src/Library.Console/Library.Console.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <AssemblyName>Library.Console</AssemblyName>
    <RootNamespace>Library.ConsoleApp</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Library.Domain/Library.Domain.csproj" />
    <ProjectReference Include="../Library.Application/Library.Application.csproj" />
    <ProjectReference Include="../Library.Infrastructure/Library.Infrastructure.csproj" />
  </ItemGroup>
</Project>
""",
"src/Library.Console/Program.cs": """using Library.Application.Services;
using Library.Domain.Inventory;
using Library.Infrastructure;
using Library.Infrastructure.Persistence;

// Temporary in-memory persistence. Replace with SQLite implementation later.
var repository = new InMemoryInventoryRepository();
var loader = new InventoryLoader(repository);
var inventory = await loader.LoadAsync();

var service = new LibraryService(inventory, repository);

Console.WriteLine("Library System");
Console.WriteLine("1. Add book");
Console.WriteLine("2. Add copy");
Console.WriteLine("3. Find book");
Console.Write("Choose: ");

switch (Console.ReadLine())
{
    case "1":
        Console.Write("Book ID: ");
        if (!int.TryParse(Console.ReadLine(), out var bookId))
        {
            Console.WriteLine("Invalid ID.");
            break;
        }

        Console.Write("Book name: ");
        var name = Console.ReadLine() ?? string.Empty;

        var book = await service.AddBookAsync(bookId, name);
        Console.WriteLine($"Added book: {book.Id} - {book.Name}");
        break;

    case "2":
        Console.Write("Copy ID: ");
        if (!int.TryParse(Console.ReadLine(), out var copyId))
        {
            Console.WriteLine("Invalid copy ID.");
            break;
        }

        Console.Write("Book ID: ");
        if (!int.TryParse(Console.ReadLine(), out var parentBookId))
        {
            Console.WriteLine("Invalid book ID.");
            break;
        }

        var copy = await service.AddCopyAsync(copyId, parentBookId);
        Console.WriteLine($"Added copy {copy.Id} for '{copy.Book.Name}'.");
        break;

    case "3":
        Console.Write("Book ID: ");
        if (int.TryParse(Console.ReadLine(), out var searchId))
        {
            try
            {
                var found = service.GetBook(searchId);
                Console.WriteLine($"{found.Id} - {found.Name}");
            }
            catch (KeyNotFoundException ex)
            {
                Console.WriteLine(ex.Message);
            }
        }
        break;

    default:
        Console.WriteLine("Unknown option.");
        break;
}
""",
"tests/Library.Tests/Library.Tests.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
    <AssemblyName>Library.Tests</AssemblyName>
    <RootNamespace>Library.Tests</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.12.0" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="../../src/Library.Domain/Library.Domain.csproj" />
  </ItemGroup>
</Project>
""",
"tests/Library.Tests/InventoryTests.cs": """using Library.Domain.Inventory;

namespace Library.Tests;

public sealed class InventoryTests
{
    [Fact]
    public void AddCopy_WhenBookDoesNotExist_Throws()
    {
        var inventory = new Inventory();

        Assert.Throws<KeyNotFoundException>(() => inventory.AddCopy(100, 999));
    }

    [Fact]
    public void AddCopy_WhenBookExists_UsesTheSameBookObject()
    {
        var inventory = new Inventory();
        var book = inventory.AddBook(1, "Clean Code");

        var copy = inventory.AddCopy(100, 1);

        Assert.Same(book, copy.Book);
    }

    [Fact]
    public void AddBook_WhenIdAlreadyExists_Throws()
    {
        var inventory = new Inventory();
        inventory.AddBook(1, "Clean Code");

        Assert.Throws<InvalidOperationException>(() => inventory.AddBook(1, "Different title"));
    }
}
"""
}
# remove stale generated folder if any
import shutil
if os.path.exists(root):
    shutil.rmtree(root)
for rel, content in files.items():
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

zip_path = "/mnt/data/LibrarySystem-scaffold.zip"
if os.path.exists(zip_path):
    os.remove(zip_path)
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for base, dirs, names in os.walk(root):
        for name in names:
            p = os.path.join(base, name)
            z.write(p, os.path.relpath(p, root))

print(f"Created scaffold with {len(files)} files.")
print(zip_path)

root = "/mnt/data/LibrarySystem"
files = {
"LibrarySystem.sln": """Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Domain", "src\\Library.Domain\\Library.Domain.csproj", "{A1111111-1111-4111-8111-111111111111}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Application", "src\\Library.Application\\Library.Application.csproj", "{A2222222-2222-4222-8222-222222222222}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Infrastructure", "src\\Library.Infrastructure\\Library.Infrastructure.csproj", "{A3333333-3333-4333-8333-333333333333}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Console", "src\\Library.Console\\Library.Console.csproj", "{A4444444-4444-4444-8444-444444444444}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Library.Tests", "tests\\Library.Tests\\Library.Tests.csproj", "{A5555555-5555-4555-8555-555555555555}"
EndProject
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
        Debug|Any CPU = Debug|Any CPU
        Release|Any CPU = Release|Any CPU
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
        {A1111111-1111-4111-8111-111111111111}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A1111111-1111-4111-8111-111111111111}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A1111111-1111-4111-8111-111111111111}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A1111111-1111-4111-8111-111111111111}.Release|Any CPU.Build.0 = Release|Any CPU
        {A2222222-2222-4222-8222-222222222222}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A2222222-2222-4222-8222-222222222222}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A2222222-2222-4222-8222-222222222222}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A2222222-2222-4222-8222-222222222222}.Release|Any CPU.Build.0 = Release|Any CPU
        {A3333333-3333-4333-8333-333333333333}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A3333333-3333-4333-8333-333333333333}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A3333333-3333-4333-8333-333333333333}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A3333333-3333-4333-8333-333333333333}.Release|Any CPU.Build.0 = Release|Any CPU
        {A4444444-4444-4444-8444-444444444444}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A4444444-4444-4444-8444-444444444444}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A4444444-4444-4444-8444-444444444444}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A5555555-5555-4555-8555-555555555555}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {A5555555-5555-4555-8555-555555555555}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {A5555555-5555-4555-8555-555555555555}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {A5555555-5555-4555-8555-555555555555}.Release|Any CPU.Build.0 = Release|Any CPU
    EndGlobalSection
EndGlobal
""",
"Directory.Build.props": """<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>
</Project>
""",
"README.md": """# LibrarySystem

Small library inventory project scaffold in C#/.NET.

## Projects
- `Library.Domain`: domain entities and inventory invariants; no I/O dependencies.
- `Library.Application`: application use cases and repository contracts.
- `Library.Infrastructure`: in-memory persistence adapter for the initial scaffold.
- `Library.Console`: composition root / command-line entry point.
- `Library.Tests`: unit tests for domain behavior.

## Run
```bash
dotnet restore
dotnet build
dotnet test
dotnet run --project src/Library.Console
```

## Initial design decisions
- `Book` represents a bibliographic title.
- `BookCopy` represents one physical copy.
- `Inventory` is the in-memory authority for creating books and copies.
- `Book` and `BookCopy` constructors are `internal` to discourage creation outside the domain assembly. This is an assembly-level restriction, not a security boundary.
- This scaffold intentionally uses in-memory storage. Add SQLite/database I/O behind the application repository interfaces later.
- A production database must enforce concurrency-sensitive invariants too; an in-memory dictionary alone cannot protect multiple processes or application instances.
""",
"src/Library.Domain/Library.Domain.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>Library.Domain</AssemblyName>
    <RootNamespace>Library.Domain</RootNamespace>
  </PropertyGroup>
</Project>
""",
"src/Library.Domain/Entities/Book.cs": """namespace Library.Domain.Entities;

public sealed class Book
{
    public int Id { get; }
    public string Name { get; }

    internal Book(int id, string name)
    {
        if (id <= 0)
            throw new ArgumentOutOfRangeException(nameof(id), "Book ID must be positive.");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Book name cannot be empty.", nameof(name));

        Id = id;
        Name = name.Trim();
    }
}
""",
"src/Library.Domain/Entities/BookCopy.cs": """namespace Library.Domain.Entities;

public enum BookCopyStatus
{
    Available,
    Borrowed,
    Maintenance,
    Lost
}

public sealed class BookCopy
{
    public int Id { get; }
    public Book Book { get; }
    public BookCopyStatus Status { get; private set; }

    internal BookCopy(int id, Book book)
    {
        if (id <= 0)
            throw new ArgumentOutOfRangeException(nameof(id));

        ArgumentNullException.ThrowIfNull(book);

        Id = id;
        Book = book;
        Status = BookCopyStatus.Available;
    }

    public void MarkBorrowed()
    {
        if (Status != BookCopyStatus.Available)
            throw new InvalidOperationException("Only available copies can be borrowed.");

        Status = BookCopyStatus.Borrowed;
    }

    public void MarkReturned()
    {
        if (Status != BookCopyStatus.Borrowed)
            throw new InvalidOperationException("Only borrowed copies can be returned.");

        Status = BookCopyStatus.Available;
    }
}
""",
"src/Library.Domain/Inventory/Inventory.cs": """using Library.Domain.Entities;

namespace Library.Domain.Inventory;

public sealed class Inventory
{
    private readonly Dictionary<int, Book> _books = new();
    private readonly Dictionary<int, BookCopy> _copies = new();

    public IReadOnlyCollection<Book> Books => _books.Values;
    public IReadOnlyCollection<BookCopy> Copies => _copies.Values;

    public Book AddBook(int id, string name)
    {
        if (_books.ContainsKey(id))
            throw new InvalidOperationException($"A book with ID {id} already exists.");

        var book = new Book(id, name);
        _books.Add(id, book);
        return book;
    }

    public Book GetBook(int bookId)
    {
        if (!_books.TryGetValue(bookId, out var book))
            throw new KeyNotFoundException($"Book {bookId} was not found.");

        return book;
    }

    public BookCopy AddCopy(int copyId, int bookId)
    {
        if (_copies.ContainsKey(copyId))
            throw new InvalidOperationException($"A copy with ID {copyId} already exists.");

        var book = GetBook(bookId);
        var copy = new BookCopy(copyId, book);
        _copies.Add(copyId, copy);
        return copy;
    }

    public BookCopy GetCopy(int copyId)
    {
        if (!_copies.TryGetValue(copyId, out var copy))
            throw new KeyNotFoundException($"Copy {copyId} was not found.");

        return copy;
    }
}
""",
"src/Library.Application/Library.Application.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>Library.Application</AssemblyName>
    <RootNamespace>Library.Application</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Library.Domain/Library.Domain.csproj" />
  </ItemGroup>
</Project>
""",
"src/Library.Application/Abstractions/IInventoryRepository.cs": """using Library.Domain.Entities;

namespace Library.Application.Abstractions;

/// <summary>
/// Persistence contract. Implementations can use SQLite, PostgreSQL, or another store.
/// </summary>
public interface IInventoryRepository
{
    Task<IReadOnlyList<BookRecord>> LoadBooksAsync(CancellationToken cancellationToken = default);
    Task<IReadOnlyList<BookCopyRecord>> LoadCopiesAsync(CancellationToken cancellationToken = default);
    Task SaveBookAsync(BookRecord book, CancellationToken cancellationToken = default);
    Task SaveCopyAsync(BookCopyRecord copy, CancellationToken cancellationToken = default);
}

public sealed record BookRecord(int Id, string Name);
public sealed record BookCopyRecord(int Id, int BookId, BookCopyStatus Status);
""",
"src/Library.Application/Services/LibraryService.cs": """using Library.Application.Abstractions;
using Library.Domain.Entities;
using Library.Domain.Inventory;

namespace Library.Application.Services;

public sealed class LibraryService
{
    private readonly Inventory _inventory;
    private readonly IInventoryRepository _repository;

    public LibraryService(Inventory inventory, IInventoryRepository repository)
    {
        _inventory = inventory;
        _repository = repository;
    }

    public async Task<Book> AddBookAsync(int id, string name, CancellationToken cancellationToken = default)
    {
        var book = _inventory.AddBook(id, name);
        await _repository.SaveBookAsync(new BookRecord(book.Id, book.Name), cancellationToken);
        return book;
    }

    public async Task<BookCopy> AddCopyAsync(int copyId, int bookId, CancellationToken cancellationToken = default)
    {
        var copy = _inventory.AddCopy(copyId, bookId);
        await _repository.SaveCopyAsync(
            new BookCopyRecord(copy.Id, copy.Book.Id, copy.Status), cancellationToken);
        return copy;
    }

    public Book GetBook(int id) => _inventory.GetBook(id);

    public BookCopy GetCopy(int id) => _inventory.GetCopy(id);
}
""",
"src/Library.Infrastructure/Library.Infrastructure.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>Library.Infrastructure</AssemblyName>
    <RootNamespace>Library.Infrastructure</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Library.Domain/Library.Domain.csproj" />
    <ProjectReference Include="../Library.Application/Library.Application.csproj" />
  </ItemGroup>
</Project>
""",
"src/Library.Infrastructure/Persistence/InMemoryInventoryRepository.cs": """using Library.Application.Abstractions;
using Library.Domain.Entities;

namespace Library.Infrastructure.Persistence;

/// <summary>
/// Temporary adapter: data is lost when the process exits.
/// Replace with a database-backed implementation later.
/// </summary>
public sealed class InMemoryInventoryRepository : IInventoryRepository
{
    private readonly Dictionary<int, BookRecord> _books = new();
    private readonly Dictionary<int, BookCopyRecord> _copies = new();

    public Task<IReadOnlyList<BookRecord>> LoadBooksAsync(CancellationToken cancellationToken = default)
        => Task.FromResult<IReadOnlyList<BookRecord>>(_books.Values.ToArray());

    public Task<IReadOnlyList<BookCopyRecord>> LoadCopiesAsync(CancellationToken cancellationToken = default)
        => Task.FromResult<IReadOnlyList<BookCopyRecord>>(_copies.Values.ToArray());

    public Task SaveBookAsync(BookRecord book, CancellationToken cancellationToken = default)
    {
        if (!_books.TryAdd(book.Id, book))
            throw new InvalidOperationException($"Book {book.Id} already exists in storage.");

        return Task.CompletedTask;
    }

    public Task SaveCopyAsync(BookCopyRecord copy, CancellationToken cancellationToken = default)
    {
        if (!_books.ContainsKey(copy.BookId))
            throw new KeyNotFoundException($"Book {copy.BookId} does not exist in storage.");

        if (!_copies.TryAdd(copy.Id, copy))
            throw new InvalidOperationException($"Copy {copy.Id} already exists in storage.");

        return Task.CompletedTask;
    }
}
""",
"src/Library.Infrastructure/InventoryLoader.cs": """using Library.Application.Abstractions;
using Library.Domain.Inventory;

namespace Library.Infrastructure;

/// <summary>
/// Loads stored records into the in-memory domain inventory at startup.
/// </summary>
public sealed class InventoryLoader
{
    private readonly IInventoryRepository _repository;

    public InventoryLoader(IInventoryRepository repository) => _repository = repository;

    public async Task<Inventory> LoadAsync(CancellationToken cancellationToken = default)
    {
        var inventory = new Inventory();
        var books = await _repository.LoadBooksAsync(cancellationToken);
        var copies = await _repository.LoadCopiesAsync(cancellationToken);

        foreach (var book in books)
            inventory.AddBook(book.Id, book.Name);

        foreach (var copy in copies)
        {
            var loadedCopy = inventory.AddCopy(copy.Id, copy.BookId);
            // Restore persisted status through domain behavior rather than public setters.
            if (copy.Status == Library.Domain.Entities.BookCopyStatus.Borrowed)
                loadedCopy.MarkBorrowed();
        }

        return inventory;
    }
}
""",
"src/Library.Console/Library.Console.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <AssemblyName>Library.Console</AssemblyName>
    <RootNamespace>Library.ConsoleApp</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Library.Domain/Library.Domain.csproj" />
    <ProjectReference Include="../Library.Application/Library.Application.csproj" />
    <ProjectReference Include="../Library.Infrastructure/Library.Infrastructure.csproj" />
  </ItemGroup>
</Project>
""",
"src/Library.Console/Program.cs": """using Library.Application.Services;
using Library.Domain.Inventory;
using Library.Infrastructure;
using Library.Infrastructure.Persistence;

// Temporary in-memory persistence. Replace with SQLite implementation later.
var repository = new InMemoryInventoryRepository();
var loader = new InventoryLoader(repository);
var inventory = await loader.LoadAsync();

var service = new LibraryService(inventory, repository);

Console.WriteLine("Library System");
Console.WriteLine("1. Add book");
Console.WriteLine("2. Add copy");
Console.WriteLine("3. Find book");
Console.Write("Choose: ");

switch (Console.ReadLine())
{
    case "1":
        Console.Write("Book ID: ");
        if (!int.TryParse(Console.ReadLine(), out var bookId))
        {
            Console.WriteLine("Invalid ID.");
            break;
        }

        Console.Write("Book name: ");
        var name = Console.ReadLine() ?? string.Empty;

        var book = await service.AddBookAsync(bookId, name);
        Console.WriteLine($"Added book: {book.Id} - {book.Name}");
        break;

    case "2":
        Console.Write("Copy ID: ");
        if (!int.TryParse(Console.ReadLine(), out var copyId))
        {
            Console.WriteLine("Invalid copy ID.");
            break;
        }

        Console.Write("Book ID: ");
        if (!int.TryParse(Console.ReadLine(), out var parentBookId))
        {
            Console.WriteLine("Invalid book ID.");
            break;
        }

        var copy = await service.AddCopyAsync(copyId, parentBookId);
        Console.WriteLine($"Added copy {copy.Id} for '{copy.Book.Name}'.");
        break;

    case "3":
        Console.Write("Book ID: ");
        if (int.TryParse(Console.ReadLine(), out var searchId))
        {
            try
            {
                var found = service.GetBook(searchId);
                Console.WriteLine($"{found.Id} - {found.Name}");
            }
            catch (KeyNotFoundException ex)
            {
                Console.WriteLine(ex.Message);
            }
        }
        break;

    default:
        Console.WriteLine("Unknown option.");
        break;
}
""",
"tests/Library.Tests/Library.Tests.csproj": """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
    <AssemblyName>Library.Tests</AssemblyName>
    <RootNamespace>Library.Tests</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.12.0" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="../../src/Library.Domain/Library.Domain.csproj" />
  </ItemGroup>
</Project>
""",
"tests/Library.Tests/InventoryTests.cs": """using Library.Domain.Inventory;

namespace Library.Tests;

public sealed class InventoryTests
{
    [Fact]
    public void AddCopy_WhenBookDoesNotExist_Throws()
    {
        var inventory = new Inventory();

        Assert.Throws<KeyNotFoundException>(() => inventory.AddCopy(100, 999));
    }

    [Fact]
    public void AddCopy_WhenBookExists_UsesTheSameBookObject()
    {
        var inventory = new Inventory();
        var book = inventory.AddBook(1, "Clean Code");

        var copy = inventory.AddCopy(100, 1);

        Assert.Same(book, copy.Book);
    }

    [Fact]
    public void AddBook_WhenIdAlreadyExists_Throws()
    {
        var inventory = new Inventory();
        inventory.AddBook(1, "Clean Code");

        Assert.Throws<InvalidOperationException>(() => inventory.AddBook(1, "Different title"));
    }
}
"""
}
# remove stale generated folder if any
import shutil
if os.path.exists(root):
    shutil.rmtree(root)
for rel, content in files.items():
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
