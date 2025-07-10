export const LoadingSpinner: React.FC = () => {
  return (
    <div className="w-full flex items-center justify-center min-h-screen">
      <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
};
