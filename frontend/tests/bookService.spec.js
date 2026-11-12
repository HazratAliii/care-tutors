// Unit test for BookService: all HTTP calls live in this one service.
describe('BookService', function () {
  var BookService, $httpBackend;
  var API = 'http://localhost:5001';

  beforeEach(module('library.services'));

  beforeEach(inject(function (_BookService_, _$httpBackend_) {
    BookService = _BookService_;
    $httpBackend = _$httpBackend_;
  }));

  afterEach(function () {
    $httpBackend.verifyNoOutstandingExpectation();
    $httpBackend.verifyNoOutstandingRequest();
  });

  it('loads books from the API with the given search and category params', function () {
    var books = [{ id: 7, title: 'Cosmos', author: 'Carl Sagan' }];
    $httpBackend
      .expectGET(API + '/api/books?search=cosmos&category=Science')
      .respond(200, books);

    var loaded;
    BookService.list({ search: 'cosmos', category: 'Science' })
      .then(function (response) {
        loaded = response.data;
      });

    $httpBackend.flush();
    expect(loaded).toEqual(books);
  });
});
