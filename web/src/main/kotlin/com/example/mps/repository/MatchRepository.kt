package com.example.mps.repository

import com.example.mps.model.MatchEntity
import org.springframework.data.repository.CrudRepository
import org.springframework.stereotype.Repository

@Repository
interface MatchRepository : CrudRepository<MatchEntity, Long>