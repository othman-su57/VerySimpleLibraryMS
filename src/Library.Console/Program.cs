using Library.Domain.Entities;
using Library.Domain.Inventory;

const int bookCount = 100;
const int copiesPerBook = 100;

Dictionary<string, Book> books = new();
Inventory inventory = new(books);

List<BookCopy> allCopies = new();
Random random = new(42);

// 1. Create books and copies.
for (int i = 0; i < bookCount; i++)
{
    Book book = new($"Book {i}", $"Description {i}");

    for (int j = 0; j < copiesPerBook; j++)
    {
        BookCopy copy = new(book, Guid.NewGuid());

        inventory.AddCopy(copy);
        allCopies.Add(copy);
    }
}

Console.WriteLine($"Created {bookCount} books.");
Console.WriteLine($"Created {allCopies.Count} copies.");

// 2. Borrow each book repeatedly.
for (int i = 0; i < copiesPerBook; i++)
{
    for (int j = 0; j < bookCount; j++)
    {
        inventory.BorrowBook($"Book {j}");
    }
}

int borrowedAfterCheckout =
    allCopies.Count(c => c.State == BookCopyState.Borrowed);

int availableAfterCheckout =
    allCopies.Count(c => c.State == BookCopyState.Available);

Console.WriteLine("\nAfter borrowing:");
Console.WriteLine($"Borrowed: {borrowedAfterCheckout}");
Console.WriteLine($"Available: {availableAfterCheckout}");

// 3. Return random copies by their IDs.
int returnAttempts = 5000;

for (int i = 0; i < returnAttempts; i++)
{
    BookCopy copy = allCopies[random.Next(allCopies.Count)];
    inventory.ReturnBook(copy.BookCopyId);
}

int borrowedAfterReturns =
    allCopies.Count(c => c.State == BookCopyState.Borrowed);

int availableAfterReturns =
    allCopies.Count(c => c.State == BookCopyState.Available);

Console.WriteLine("\nAfter random returns:");
Console.WriteLine($"Borrowed: {borrowedAfterReturns}");
Console.WriteLine($"Available: {availableAfterReturns}");

// 4. Try returning nonexistent IDs.
for (int i = 0; i < 1000; i++)
{
    inventory.ReturnBook(Guid.NewGuid());
}

Console.WriteLine("\nAfter invalid return attempts:");
Console.WriteLine(
    $"Borrowed: {allCopies.Count(c => c.State == BookCopyState.Borrowed)}"
);
Console.WriteLine(
    $"Available: {allCopies.Count(c => c.State == BookCopyState.Available)}"
);

// 5. Verify invariants.
bool allIdsUnique =
    allCopies.Select(c => c.BookCopyId).Distinct().Count() == allCopies.Count;

bool allStatesValid =
    allCopies.All(c => Enum.IsDefined(c.State));

bool allBooksRegistered =
    allCopies.All(c => books.ContainsKey(c.Book.Name));

Console.WriteLine("\nInvariant checks:");
Console.WriteLine($"All copy IDs unique: {allIdsUnique}");
Console.WriteLine($"All states valid: {allStatesValid}");
Console.WriteLine($"All books registered: {allBooksRegistered}");