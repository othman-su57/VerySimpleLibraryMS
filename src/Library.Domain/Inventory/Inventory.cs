using Library.Domain.Entities;

namespace Library.Domain.Inventory
{
    public class Inventory(Dictionary<string, Book> books)
    {
        private readonly Dictionary<string, Book> _books = books;
        private readonly List<BookCopy> _bookCopies = new();

        public void AddBook(Book book)
        {
            ArgumentNullException.ThrowIfNull(book);

            if (_books.ContainsKey(book.Name))
                return;

            _books.Add(book.Name, book);
        }

        public void AddCopy(BookCopy bookCopy)
        {
            ArgumentNullException.ThrowIfNull(bookCopy);

            if (_books.ContainsKey(bookCopy.Book.Name))
            {
                _bookCopies.Add(bookCopy);
                return;
            }

            AddBook(bookCopy.Book);
            AddCopy(bookCopy);
        }

        public void RemoveCopy(BookCopy bookCopy)
        {
            ArgumentNullException.ThrowIfNull(bookCopy);

            _bookCopies.Remove(bookCopy);
        }

        public void BorrowBook(string title)
        {
            ArgumentNullException.ThrowIfNull(title);

            if (_bookCopies.All(copy => copy.Book.Name != title))
                return;

            foreach (BookCopy copy in _bookCopies)
            {
                if (copy.Book.Name == title &&
                    copy.State == BookCopyState.Available)
                {
                    copy.Borrow();
                    return;
                }
            }
        }

        public void ReturnBook(Guid bookId)
        {

            if (_bookCopies.All(copy => copy.BookCopyId != bookId))
                return;

            foreach (BookCopy copy in _bookCopies)
            {
                if (copy.BookCopyId == bookId &&
                    copy.State == BookCopyState.Borrowed)
                {
                    copy.Return();
                    return;
                }
            }
        }
    }
}