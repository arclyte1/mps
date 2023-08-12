package com.example.mps.service

import com.example.mps.repository.MatchRepository
import org.springframework.stereotype.Service

@Service
class MatchService(
    private val repository: MatchRepository
) {

    fun getMatches(): String {
        return repository.findAll().last().id.toString()
    }
}