from typing import List, TypeVar, Generic, Tuple
from django.core.paginator import Paginator, EmptyPage
from dataclasses import dataclass

T = TypeVar('T')

class PaginationInput:
    def __init__(self, page_number: int = 1, page_size: int = 10):
        self.page_number = page_number
        self.page_size = page_size

@dataclass
class PaginationMetadata:
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
    has_next: bool
    has_previous: bool

@dataclass
class PaginatedResponse(Generic[T]):
    items: List[T]
    metadata: PaginationMetadata

    @classmethod
    def empty(cls, page: int = 1, page_size: int = 10):
        return cls(
            items=[],
            metadata=PaginationMetadata(
                total_items=0,
                total_pages=0,
                current_page=page,
                page_size=page_size,
                has_next=False,
                has_previous=False
            )
        )

class PaginationHelper:
    @staticmethod
    def get_paginated_response(
        pagination_input: PaginationInput,
        queryset=[], 
        mapper_fn=lambda x: x
    ) -> PaginatedResponse:
        try:
            paginator = Paginator(queryset, pagination_input.page_size)
            page_obj = paginator.page(pagination_input.page_number)
            
            return PaginatedResponse(
                items=[mapper_fn(item) for item in page_obj],
                metadata=PaginationMetadata(
                    total_items=paginator.count,
                    total_pages=paginator.num_pages,
                    current_page=pagination_input.page_number,
                    page_size=pagination_input.page_size,
                    has_next=page_obj.has_next(),
                    has_previous=page_obj.has_previous()
                )
            )
        except EmptyPage:
            return PaginatedResponse.empty(
                page=pagination_input.page_number, 
                page_size=pagination_input.page_size
            )


def get_pagination_data(request) -> PaginationInput:
    try:
        page_number = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
    except ValueError:
        page_number = 1
        page_size = 10

    return PaginationInput(page_number=page_number, page_size=page_size)