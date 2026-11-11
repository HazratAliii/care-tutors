/* All HTTP calls for the books API live in this one service. */
angular.module('library.services', [])

.factory('BookService', ['$http', function ($http) {
  var API_BASE = 'http://localhost:5001';

  return {
    list: function (params) {
      return $http.get(API_BASE + '/api/books', { params: params });
    },
    get: function (id) {
      return $http.get(API_BASE + '/api/books/' + id);
    },
    create: function (book) {
      return $http.post(API_BASE + '/api/books', book);
    },
    update: function (id, book) {
      return $http.put(API_BASE + '/api/books/' + id, book);
    },
    remove: function (id) {
      return $http.delete(API_BASE + '/api/books/' + id);
    },
    borrow: function (id, borrowerName) {
      return $http.post(API_BASE + '/api/books/' + id + '/borrow',
        { borrower_name: borrowerName });
    },
    returnBook: function (id) {
      return $http.post(API_BASE + '/api/books/' + id + '/return');
    }
  };
}]);
