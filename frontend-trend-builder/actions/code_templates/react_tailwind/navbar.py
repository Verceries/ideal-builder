TEMPLATE = """
const Navbar = () => {
  return (
    <nav className="p-4 bg-white shadow-sm">
      <div className="container mx-auto flex items-center justify-between">
        <div className="text-xl font-bold text-blue-600">
          Logo
        </div>
        <ul className="flex items-center">
          <li>
            <a href="#home" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">Home</a>
          </li>
          <li>
            <a href="#about" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">About</a>
          </li>
          <li>
            <a href="#contact" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">Contact</a>
          </li>
        </ul>
        <div>
          {/* CTA Button can be added here if needed */}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
"""
