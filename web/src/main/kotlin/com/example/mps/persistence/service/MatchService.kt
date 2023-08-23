package com.example.mps.persistence.service

import com.example.mps.domain.model.Match
import com.example.mps.domain.repository.MatchRepository
import org.springframework.stereotype.Service

@Service
class MatchService(
    private val repository: MatchRepository
) {

    fun getMatches(): List<Match> {
        return repository.findAll().map { it.toMatch() }
    }
}