import { useQuery } from '@tanstack/react-query'
import { getProducts } from '../services/api'

export default function Products() {
  const { data: products, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: () => getProducts(),
  })

  if (isLoading) {
    return <div className="px-4 py-6 text-gray-600 dark:text-gray-400">Loading products...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Products</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Manage your product catalog
          </p>
        </div>
        <button className="bg-blue-600 dark:bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-700 dark:hover:bg-blue-600">
          Add Product
        </button>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {products && products.length > 0 ? (
            products.map((product) => (
              <li key={product.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {product.name}
                      </p>
                      {product.sku && (
                        <p className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                          SKU: {product.sku}
                        </p>
                      )}
                    </div>
                    <div className="ml-2 flex-shrink-0 flex">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        ${product.price.toFixed(2)}
                      </p>
                    </div>
                  </div>
                  {product.description && (
                    <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                      {product.description}
                    </p>
                  )}
                  <div className="mt-2 flex items-center space-x-4">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      Quantity: {product.quantity}
                    </span>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        product.status === 'active'
                          ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                          : product.status === 'draft'
                          ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                      }`}
                    >
                      {product.status}
                    </span>
                  </div>
                </div>
              </li>
            ))
          ) : (
            <li className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
              No products found. Create your first product to get started.
            </li>
          )}
        </ul>
      </div>
    </div>
  )
}

