TEMPLATE = """
const Footer = () => {
  return (
    <footer className="bg-gray-100 text-gray-700 py-12">
      <div className="container mx-auto px-4">
        {/* Link columns can be added here if needed */}
        <div className="mt-8 border-t border-gray-200 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-base text-gray-500">
            © 2024 Your Company
          </p>
          <div className="flex items-center mt-4 md:mt-0">
            {/* Social links can be added here */}
            <a href="#twitter" className="text-gray-500 hover:text-blue-600 ml-4">
              Twitter {/* Replace with actual icons */}
            </a>
            <a href="#github" className="text-gray-500 hover:text-blue-600 ml-4">
              GitHub {/* Replace with actual icons */}
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
"""
