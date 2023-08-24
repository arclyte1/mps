package com.example.mps.domain.repository

import com.example.mps.persistence.model.MatchEntity
import org.springframework.data.repository.PagingAndSortingRepository
import org.springframework.stereotype.Repository

@Repository
interface MatchRepository : PagingAndSortingRepository<MatchEntity, Long>