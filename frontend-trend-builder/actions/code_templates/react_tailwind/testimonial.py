TEMPLATE = """
const Testimonial = () => {
  return (
    <div className="bg-gray-50 p-6 rounded-lg shadow">
      <blockquote className="text-gray-600 italic mb-4">
        "This is a fantastic product!"
      </blockquote>
      <div className="flex items-center">
        {/* Author Image Placeholder can be added here */}
        <div>
          <p className="font-semibold text-gray-900">Jane Doe</p>
          <p className="text-sm text-gray-500">CEO, ExampleCo</p>
        </div>
      </div>
    </div>
  );
};

export default Testimonial;
"""
