#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "CVector.h"

int vector_init(Vector *v, size_t capacity) {
    assert(v != NULL);
    v->capacity = MAX(VECTOR_INIT_CAPACITY, capacity);
    v->length = 0;
    v->data = malloc(sizeof(void *) * v->capacity);
    return v->data == NULL ? VECTOR_ERROR : VECTOR_SUCCESS;
}

size_t vector_length(Vector *v) {
    return v->length;
}

static void vector_resize(Vector *v, int capacity) {
    #ifdef DEBUG_ON
    printf("vector_resize: %d to %d\n", v->capacity, capacity);
    #endif

    void **data = realloc(v->data, sizeof(void *) * capacity);
    if (data) {
        v->data = data;
        v->capacity = capacity;
    }
}

void vector_add(Vector *v, void *item) {
    if (v->capacity == v->length)
        vector_resize(v, v->capacity * 2);
    v->data[v->length++] = item;
}

void vector_set(Vector *v, int index, void *item) {
    if (index >= 0 && index < v->length)
        v->data[index] = item;
}

void* vector_get(Vector *v, int index) {
    if (index >= 0 && index < v->length)
        return v->data[index];
    return NULL;
}

void vector_delete(Vector *v, int index)
{
    if (index < 0 || index >= v->length)
        return;

    v->data[index] = NULL;
    int i;
    for (i = index; i < v->length - 1; i++) {
        v->data[i] = v->data[i + 1];
        v->data[i + 1] = NULL;
    }

    v->length--;

    if (v->length > 0 && v->length == v->capacity / 4)
        vector_resize(v, v->capacity / 2);
}

void vector_free(Vector *v)
{
    free(v->data);
}