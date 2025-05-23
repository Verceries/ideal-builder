TEMPLATE = """
const HeroSection = () => {
  return (
    <section className="bg-gray-50 py-12 sm:py-20 relative">
      {/* Background Image Placeholder can be added here if needed */}
      <div className="container mx-auto px-4 text-center">
        <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
          Main Heading
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Subheading text...
        </p>
        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          <div className="rounded-md shadow">
            <a href="#" className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10">
              Get Started
            </a>
          </div>
          {/* Secondary CTA can be added here if needed */}
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
"""
