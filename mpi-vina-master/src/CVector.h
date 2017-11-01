#ifndef CVECTOR_H
#define CVECTOR_H

#define VECTOR_INIT_CAPACITY 4
#define VECTOR_ERROR -1
#define VECTOR_SUCCESS 0


#define VECTOR_INIT(vec, capacity) Vector vec; vector_init(&vec, capacity)
#define VECTOR_ADD(vec, item) vector_add(&vec, (void *) item)
#define VECTOR_SET(vec, id, item) vector_set(&vec, id, (void *) item)
#define VECTOR_GET(vec, type, id) (type) vector_get(&vec, id)
#define VECTOR_DELETE(vec, id) vector_delete(&vec, id)
#define VECTOR_LEN(vec) vector_length(&vec)
#define VECTOR_FREE(vec) vector_free(&vec)

#define MAX(a,b) (((a)>(b))?(a):(b))

typedef struct vector {
    void **data;
    int capacity;
    int length;
} Vector;

int vector_init(Vector *v, size_t);
int vector_total(Vector *);
static void vector_resize(Vector *, int);
void vector_add(Vector *, void *);
void vector_set(Vector *, int, void *);
void *vector_get(Vector *, int);
void vector_delete(Vector *, int);
size_t vector_length(Vector *);
void vector_free(Vector *);

#endif