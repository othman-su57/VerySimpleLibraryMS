using System.Runtime.CompilerServices;

namespace Library.Domain.Entities
{
    public class BookCopy(Book book, Guid bookCopyId)
    {
        public Book Book { get; set; } = book;
        public BookCopyState State { get; set; }  = BookCopyState.Available;
        public Guid BookCopyId { get; set; } = bookCopyId;
        
        public void Borrow()
        {
            if (this.State == BookCopyState.Available){
                this.State = BookCopyState.Borrowed;
            }
        }

        public void Return()
        {
            if (this.State == BookCopyState.Borrowed)
            {
                this.State = BookCopyState.Available;
            }
        }
    }

}


public enum BookCopyState
{
    Available,
    Borrowed
}