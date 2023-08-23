package com.example.mps.domain.repository

import com.example.mps.persistence.model.MatchEntity
import org.springframework.data.repository.CrudRepository
import org.springframework.stereotype.Repository

@Repository
interface MatchRepository : CrudRepository<MatchEntity, Long>