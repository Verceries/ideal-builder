TEMPLATE = """
const FeatureCard = ({ title, description, icon }) => {
  return (
    <div className="bg-white shadow-lg rounded-lg p-6 flex flex-col items-center text-center">
      {icon && <div className="text-blue-500 mb-4">{icon}</div>}
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title || "Feature Title"}</h3>
      <p className="text-gray-600 text-base">
        {description || "Feature description."}
      </p>
      {/* Learn More Link can be added here if needed */}
    </div>
  );
};

// Example of how a features section might use this card:
const FeaturesSection = () => {
  // Example icon (replace with actual SVGs or an icon library in a real app)
  const PlaceholderIcon = () => (
    <svg className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
    </svg>
  );

  const features = [
    { title: "Fast Performance", description: "Optimized for speed and efficiency.", icon: <PlaceholderIcon /> },
    { title: "Beautiful Design", description: "Modern and intuitive user interface.", icon: <PlaceholderIcon /> },
    { title: "Easy to Use", description: "Simple and straightforward to get started.", icon: <PlaceholderIcon /> },
  ];

  return (
    <section className="py-12 bg-gray-50">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-10">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <FeatureCard key={index} title={feature.title} description={feature.description} icon={feature.icon} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection; // Or export FeatureCard if it's to be used individually elsewhere
"""
