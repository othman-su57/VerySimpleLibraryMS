namespace Library.Domain.Entities
{
    public class Book( string name, string description)
    {
        public string Name { get; } = name;
        public string Description { get; } = description;
    }
}

